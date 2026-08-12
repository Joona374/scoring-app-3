import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.db_manager import get_db_session
from db.models import (
    Player, Team, PlayerStatsTag, PlayerStatsTagOnIce, 
    PlayerStatsTagParticipating, ShotResultTypes, GameInRoster, User, Positions, ShotResult
)
from db.pydantic_schema.player_page import (
    PlayerStatsResponse,
    PlayerTagData,
    PlayerGameMetadata,
    GameTrendPoint,
    SpiderChartData,
    SpiderChartKPI,
    SynergyData,
    SynergyDataPoint,
    ChemistrySectionData,
    ChemistryTeammate,
    GameLogEntry,
)

from utils import get_current_user_and_team, ensure_team_owns_player, ensure_player_exists
from routes.players.endpoints.stats.data_collectors import get_player_all_games, get_player_tags, build_all_player_tags

router = APIRouter()


def calculate_trend_data(db: Session, team_id: int, player_id: int, player_position: Positions, all_games: list[PlayerGameMetadata], shooter_tags: list[PlayerStatsTag]) -> list[GameTrendPoint]:
    games_asc = sorted(all_games, key=lambda x: x.date); game_ids = [g.game_id for g in games_asc]
    player_game_stats = {g_id: {"goals": 0, "chances": 0} for g_id in game_ids}
    for tag in shooter_tags:
        if tag.game_id in player_game_stats:
            result = tag.shot_result.value
            if result == ShotResultTypes.GOAL_FOR: player_game_stats[tag.game_id]["goals"] += 1; player_game_stats[tag.game_id]["chances"] += 1
            elif result == ShotResultTypes.CHANCE_FOR: player_game_stats[tag.game_id]["chances"] += 1
    peers = db.query(Player).filter(Player.team_id == team_id, Player.position == player_position).all(); peer_ids = [p.id for p in peers]
    roster_entries = db.query(GameInRoster).filter(GameInRoster.game_id.in_(game_ids), GameInRoster.player_id.in_(peer_ids)).all()
    peers_present_per_game = {g_id: 0 for g_id in game_ids}
    for entry in roster_entries: peers_present_per_game[entry.game_id] += 1
    peer_tags = db.query(PlayerStatsTag).filter(PlayerStatsTag.game_id.in_(game_ids), PlayerStatsTag.shooter_id.in_(peer_ids)).all()
    peer_game_totals = {g_id: {"goals": 0, "chances": 0} for g_id in game_ids}
    for tag in peer_tags:
        result = tag.shot_result.value
        if result == ShotResultTypes.GOAL_FOR: peer_game_totals[tag.game_id]["goals"] += 1; peer_game_totals[tag.game_id]["chances"] += 1
        elif result == ShotResultTypes.CHANCE_FOR: peer_game_totals[tag.game_id]["chances"] += 1
    peer_game_avgs = {}
    for g_id in game_ids:
        count = peers_present_per_game[g_id]
        if count > 0: peer_game_avgs[g_id] = {"goals": peer_game_totals[g_id]["goals"] / count, "chances": peer_game_totals[g_id]["chances"] / count}
        else: peer_game_avgs[g_id] = {"goals": 0.0, "chances": 0.0}
    result = []
    for i, g in enumerate(games_asc):
        window_indices = list(range(max(0, i-4), i+1)); window_games = [games_asc[idx] for idx in window_indices]
        rolling_goals = sum(player_game_stats[wg.game_id]["goals"] for wg in window_games) / len(window_games)
        rolling_chances = sum(player_game_stats[wg.game_id]["chances"] for wg in window_games) / len(window_games)
        team_rolling_goals = sum(peer_game_avgs[wg.game_id]["goals"] for wg in window_games) / len(window_games)
        team_rolling_chances = sum(peer_game_avgs[wg.game_id]["chances"] for wg in window_games) / len(window_games)
        result.append(GameTrendPoint(game_id=g.game_id, opponent=g.opponent, date=g.date, goals=player_game_stats[g.game_id]["goals"], chances=player_game_stats[g.game_id]["chances"], rolling_goals=round(rolling_goals, 2), rolling_chances=round(rolling_chances, 2), team_rolling_goals=round(team_rolling_goals, 2), team_rolling_chances=round(team_rolling_chances, 2)))
    return result

def calculate_spider_data(db: Session, team_id: int, player_id: int, shooter_tags: list[PlayerStatsTag], on_ice_tags: list[PlayerStatsTag], participating_tags: list[PlayerStatsTag], all_games: list[PlayerGameMetadata]) -> SpiderChartData:
    num_games = len(all_games)
    if num_games == 0: return SpiderChartData(kpis=[])
    player_goals = sum(1 for t in shooter_tags if t.shot_result.value == ShotResultTypes.GOAL_FOR); gpg = player_goals / num_games
    player_chances_p = sum(1 for t in participating_tags if t.shot_result.value in [ShotResultTypes.GOAL_FOR, ShotResultTypes.CHANCE_FOR]); cpg = player_chances_p / num_games
    v5v5_for = sum(1 for t in on_ice_tags if t.strengths == "ES" and t.shot_result.value in [ShotResultTypes.GOAL_FOR, ShotResultTypes.CHANCE_FOR]); v5v5_against = sum(1 for t in on_ice_tags if t.strengths == "ES" and t.shot_result.value in [ShotResultTypes.GOAL_AGAINST, ShotResultTypes.CHANCE_AGAINST]); total_5v5 = v5v5_for + v5v5_against; corsi = (v5v5_for / total_5v5 * 100) if total_5v5 > 0 else 50.0
    pp_goals = sum(1 for t in on_ice_tags if t.strengths == "PP" and t.shot_result.value == ShotResultTypes.GOAL_FOR); pp_chances = sum(1 for t in on_ice_tags if t.strengths == "PP" and t.shot_result.value in [ShotResultTypes.GOAL_FOR, ShotResultTypes.CHANCE_FOR]); pp_eff = (pp_goals / pp_chances * 100) if pp_chances > 0 else 0.0
    pk_chances = sum(1 for t in on_ice_tags if t.strengths == "PK" and t.shot_result.value in [ShotResultTypes.GOAL_AGAINST, ShotResultTypes.CHANCE_AGAINST]); pk_workload = pk_chances / num_games
    all_team_players = db.query(Player).filter(Player.team_id == team_id, Player.position != Positions.GOALIE).all(); player_ids = [p.id for p in all_team_players]
    team_roster_count = db.query(func.count(GameInRoster.game_id)).filter(GameInRoster.player_id.in_(player_ids)).scalar() or 1
    team_shooter_tags = db.query(PlayerStatsTag).filter(PlayerStatsTag.shooter_id.in_(player_ids)).all(); team_goals = sum(1 for t in team_shooter_tags if t.shot_result.value == ShotResultTypes.GOAL_FOR); team_gpg = team_goals / team_roster_count
    team_participating_count = db.query(func.count(PlayerStatsTagParticipating.player_id)).select_from(PlayerStatsTagParticipating).join(PlayerStatsTag).filter(PlayerStatsTagParticipating.player_id.in_(player_ids), PlayerStatsTag.shot_result_id.in_(db.query(ShotResult.id).filter(ShotResult.value.in_([ShotResultTypes.GOAL_FOR, ShotResultTypes.CHANCE_FOR])))).scalar() or 0; team_cpg = team_participating_count / team_roster_count
    team_on_ice_metrics = db.query(PlayerStatsTag.strengths, ShotResult.value, func.count(PlayerStatsTagOnIce.player_id)).select_from(PlayerStatsTagOnIce).join(PlayerStatsTag).join(ShotResult).filter(PlayerStatsTagOnIce.player_id.in_(player_ids)).group_by(PlayerStatsTag.strengths, ShotResult.value).all(); stats = {}
    for s, r, count in team_on_ice_metrics: stats[(s, r)] = count
    team_v5v5_for = stats.get(("ES", ShotResultTypes.GOAL_FOR), 0) + stats.get(("ES", ShotResultTypes.CHANCE_FOR), 0); team_v5v5_against = stats.get(("ES", ShotResultTypes.GOAL_AGAINST), 0) + stats.get(("ES", ShotResultTypes.CHANCE_AGAINST), 0); team_corsi = (team_v5v5_for / (team_v5v5_for + team_v5v5_against) * 100) if (team_v5v5_for + team_v5v5_against) > 0 else 50.0; team_pp_goals = stats.get(("PP", ShotResultTypes.GOAL_FOR), 0); team_pp_chances = team_pp_goals + stats.get(("PP", ShotResultTypes.CHANCE_FOR), 0); team_pp_eff = (team_pp_goals / team_pp_chances * 100) if team_pp_chances > 0 else 0.0; team_pk_against = stats.get(("PK", ShotResultTypes.GOAL_AGAINST), 0) + stats.get(("PK", ShotResultTypes.CHANCE_AGAINST), 0); team_pk_workload = team_pk_against / team_roster_count
    return SpiderChartData(kpis=[SpiderChartKPI(label="Maalit / peli", player_value=round(gpg, 2), team_avg=round(team_gpg, 2)), SpiderChartKPI(label="Osallisuudet / peli", player_value=round(cpg, 2), team_avg=round(team_cpg, 2)), SpiderChartKPI(label="5v5 Corsi %", player_value=round(corsi, 1), team_avg=round(team_corsi, 1)), SpiderChartKPI(label="YV Tehokkuus %", player_value=round(pp_eff, 1), team_avg=round(team_pp_eff, 1)), SpiderChartKPI(label="AV Työkuorma", player_value=round(pk_workload, 2), team_avg=round(team_pk_workload, 2))])

def calculate_synergy_data(db: Session, team_id: int, player_id: int, all_games: list[PlayerGameMetadata]) -> SynergyData:
    game_ids = [g.game_id for g in all_games]; shared_rosters = db.query(GameInRoster).filter(GameInRoster.game_id.in_(game_ids)).all()
    teammate_shared_games = {}
    for entry in shared_rosters:
        if entry.player_id == player_id: continue
        if entry.player_id not in teammate_shared_games: teammate_shared_games[entry.player_id] = []
        teammate_shared_games[entry.player_id].append(entry.game_id)
    teammate_impact = {t_id: {"for": 0, "against": 0} for t_id in teammate_shared_games}; hero_on_ice_tags = db.query(PlayerStatsTag.id, PlayerStatsTag.shot_result_id, PlayerStatsTag.game_id).join(PlayerStatsTagOnIce).filter(PlayerStatsTagOnIce.player_id == player_id, PlayerStatsTag.game_id.in_(game_ids)).all()
    hero_on_ice_tag_ids = [t.id for t in hero_on_ice_tags]
    if not hero_on_ice_tag_ids: return SynergyData(points=[])
    teammates_on_ice = db.query(PlayerStatsTagOnIce.tag_id, PlayerStatsTagOnIce.player_id).filter(PlayerStatsTagOnIce.tag_id.in_(hero_on_ice_tag_ids)).all(); on_ice_map = {}
    for tag_id, t_id in teammates_on_ice:
        if tag_id not in on_ice_map: on_ice_map[tag_id] = set()
        on_ice_map[tag_id].add(t_id)
    res_map = {r.id: r.value for r in db.query(ShotResult).all()}
    for tag_id, res_id, game_id in hero_on_ice_tags:
        res = res_map[res_id]; is_for = res in [ShotResultTypes.GOAL_FOR, ShotResultTypes.CHANCE_FOR]; is_against = res in [ShotResultTypes.GOAL_AGAINST, ShotResultTypes.CHANCE_AGAINST]
        if not is_for and not is_against: continue
        teammates = on_ice_map.get(tag_id, set())
        for t_id in teammates:
            if t_id == player_id: continue
            if is_for: teammate_impact[t_id]["for"] += 1
            else: teammate_impact[t_id]["against"] += 1
    points = []
    players = db.query(Player).filter(Player.id.in_(list(teammate_shared_games.keys()))).all(); p_map = {p.id: p for p in players}
    for t_id, games in teammate_shared_games.items():
        if t_id not in p_map or p_map[t_id].position == Positions.GOALIE: continue
        num_shared = len(games); impact = teammate_impact[t_id]; net_mp = (impact["for"] - impact["against"]) / num_shared
        points.append(SynergyDataPoint(teammate_id=t_id, teammate_name=f"{p_map[t_id].first_name} {p_map[t_id].last_name}", jersey_number=p_map[t_id].jersey_number, net_mp_per_game=round(net_mp, 2), shared_games=num_shared))
    points.sort(key=lambda x: x.net_mp_per_game, reverse=True); return SynergyData(points=points)

def calculate_chemistry_data(db: Session, team_id: int, player_id: int, all_games: list[PlayerGameMetadata]) -> ChemistrySectionData:
    game_ids = [g.game_id for g in all_games]; rosters = db.query(GameInRoster).filter(GameInRoster.game_id.in_(game_ids)).all(); shared_games_map = {}
    for r in rosters:
        if r.player_id == player_id: continue
        shared_games_map[r.player_id] = shared_games_map.get(r.player_id, 0) + 1
    hero_p_tags = db.query(PlayerStatsTag.id, PlayerStatsTag.shot_result_id).join(PlayerStatsTagParticipating).filter(PlayerStatsTagParticipating.player_id == player_id, PlayerStatsTag.game_id.in_(game_ids)).all(); hero_p_tag_ids = [t.id for t in hero_p_tags]
    if not hero_p_tag_ids: return ChemistrySectionData(teammates=[], team_avg_volume=0, team_avg_efficiency=0)
    teammate_p = db.query(PlayerStatsTagParticipating.tag_id, PlayerStatsTagParticipating.player_id).filter(PlayerStatsTagParticipating.tag_id.in_(hero_p_tag_ids)).all(); stats_map = {}; res_map = {r.id: r.value for r in db.query(ShotResult).all()}; goal_tag_ids = {t.id for t in hero_p_tags if res_map[t.shot_result_id] == ShotResultTypes.GOAL_FOR}
    for tag_id, t_id in teammate_p:
        if t_id == player_id: continue
        if t_id not in stats_map: stats_map[t_id] = {"p": 0, "g": 0}
        stats_map[t_id]["p"] += 1
        if tag_id in goal_tag_ids: stats_map[t_id]["g"] += 1
    teammates = []; players = db.query(Player).filter(Player.id.in_(list(stats_map.keys()))).all(); p_map = {p.id: p for p in players}
    for t_id, s in stats_map.items():
        if t_id not in p_map or p_map[t_id].position == Positions.GOALIE: continue
        shared_games = shared_games_map.get(t_id, 1); p_per_game = s["p"] / shared_games; eff = (s["g"] / s["p"] * 100) if s["p"] > 0 else 0; teammates.append(ChemistryTeammate(teammate_id=t_id, name=f"{p_map[t_id].first_name} {p_map[t_id].last_name}", jersey_number=p_map[t_id].jersey_number, position=p_map[t_id].position.name, shared_games=shared_games, shared_participations=s["p"], shared_goals=s["g"], participations_per_game=round(p_per_game, 2), efficiency=round(eff, 1)))
    avg_volume = sum(t.participations_per_game for t in teammates) / len(teammates) if teammates else 0; avg_eff = sum(t.efficiency for t in teammates) / len(teammates) if teammates else 0
    return ChemistrySectionData(teammates=teammates, team_avg_volume=round(avg_volume, 2), team_avg_efficiency=round(avg_eff, 1))

def calculate_game_log(shooter_tags: list[PlayerStatsTag], on_ice_tags: list[PlayerStatsTag], participating_tags: list[PlayerStatsTag], all_games: list[PlayerGameMetadata]) -> list[GameLogEntry]:
    game_stats = {g.game_id: { "goals": 0, "chances": 0, "part_m_plus": 0, "part_m_minus": 0, "part_mp_plus": 0, "part_mp_minus": 0, "onice_m_plus": 0, "onice_m_minus": 0, "onice_mp_plus": 0, "onice_mp_minus": 0 } for g in all_games}
    for t in shooter_tags:
        if t.game_id in game_stats:
            if t.shot_result.value == ShotResultTypes.GOAL_FOR: game_stats[t.game_id]["goals"] += 1; game_stats[t.game_id]["chances"] += 1
            elif t.shot_result.value == ShotResultTypes.CHANCE_FOR: game_stats[t.game_id]["chances"] += 1
    for t in participating_tags:
        if t.game_id in game_stats:
            res = t.shot_result.value
            if res == ShotResultTypes.GOAL_FOR: game_stats[t.game_id]["part_m_plus"] += 1; game_stats[t.game_id]["part_mp_plus"] += 1
            elif res == ShotResultTypes.GOAL_AGAINST: game_stats[t.game_id]["part_m_minus"] += 1; game_stats[t.game_id]["part_mp_minus"] += 1
            elif res == ShotResultTypes.CHANCE_FOR: game_stats[t.game_id]["part_mp_plus"] += 1
            elif res == ShotResultTypes.CHANCE_AGAINST: game_stats[t.game_id]["part_mp_minus"] += 1
    for t in on_ice_tags:
        if t.game_id in game_stats:
            res = t.shot_result.value
            if res == ShotResultTypes.GOAL_FOR: game_stats[t.game_id]["onice_m_plus"] += 1; game_stats[t.game_id]["onice_mp_plus"] += 1
            elif res == ShotResultTypes.GOAL_AGAINST: game_stats[t.game_id]["onice_m_minus"] += 1; game_stats[t.game_id]["onice_mp_minus"] += 1
            elif res == ShotResultTypes.CHANCE_FOR: game_stats[t.game_id]["onice_mp_plus"] += 1
            elif res == ShotResultTypes.CHANCE_AGAINST: game_stats[t.game_id]["onice_mp_minus"] += 1
    log = []
    for g in all_games:
        s = game_stats[g.game_id]; eff = (s["goals"] / s["chances"] * 100) if s["chances"] > 0 else 0
        log.append(GameLogEntry(game_id=g.game_id, date=g.date, opponent=g.opponent, home=g.home, goals=s["goals"], chances=s["chances"], efficiency=round(eff, 1), part_m_plus=s["part_m_plus"], part_m_minus=s["part_m_minus"], part_m_diff=s["part_m_plus"] - s["part_m_minus"], part_mp_plus=s["part_mp_plus"], part_mp_minus=s["part_mp_minus"], part_mp_diff=s["part_mp_plus"] - s["part_mp_minus"], onice_m_plus=s["onice_m_plus"], onice_m_minus=s["onice_m_minus"], onice_m_diff=s["onice_m_plus"] - s["onice_m_minus"], onice_mp_plus=s["onice_mp_plus"], onice_mp_minus=s["onice_mp_minus"], onice_mp_diff=s["onice_mp_plus"] - s["onice_mp_minus"]))
    return log

def build_stats_response_for_player(player: Player, team: Team, db: Session) -> PlayerStatsResponse:
    # 1. Get the player's games and tags
    all_games = get_player_all_games(db, player.id)

    shooter_tags, on_ice_tags, participating_tags = get_player_tags(db, player.id)

    all_tags: list[PlayerTagData] = build_all_player_tags(shooter_tags, on_ice_tags, participating_tags)

    trend_data = calculate_trend_data(db, team.id, player.id, player.position, all_games, shooter_tags)

    spider_data = calculate_spider_data(db, team.id, player.id, shooter_tags, on_ice_tags, participating_tags, all_games)
    
    synergy_data = calculate_synergy_data(db, team.id, player.id, all_games)

    chemistry_data = calculate_chemistry_data(db, team.id, player.id, all_games)

    game_log = calculate_game_log(shooter_tags, on_ice_tags, participating_tags, all_games)

    return PlayerStatsResponse(
        player_id=player.id,
        first_name=player.first_name,
        last_name=player.last_name,
        jersey_number=player.jersey_number,
        position=player.position.name,
        team_name=player.team.name if player.team else "No Team",
        all_tags=all_tags,
        all_games=all_games,
        trend_data=trend_data,
        spider_data=spider_data,
        synergy_data=synergy_data,
        chemistry_data=chemistry_data,
        game_log=game_log,
    )


@router.get("/{player_id}/stats", response_model=PlayerStatsResponse)
def get_player_stats(player_id: int, db: Session = Depends(get_db_session), user_and_team: tuple[User, Team] = Depends(get_current_user_and_team)):
    _, team = user_and_team
    player = ensure_player_exists(player_id, db)
    ensure_team_owns_player(player, team)
    return build_stats_response_for_player(player, team, db)
