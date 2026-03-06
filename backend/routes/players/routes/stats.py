from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Tuple, Set
from db.db_manager import get_db_session
from db.models import (
    Player, Team, PlayerStatsTag, PlayerStatsTagOnIce, 
    PlayerStatsTagParticipating, ShotResultTypes, GameInRoster, User, Game, Positions, ShotResult
)
from db.pydantic_schemas import (
    PlayerStatsResponse, SeasonSummaryKPIs, ZoneData, MarkerData, 
    PlayerTagData, PlayerGameMetadata, ShotTypeStats, GameTrendPoint,
    SpiderChartData, SpiderChartKPI
)
from utils import get_current_user_and_team

router = APIRouter()

def get_player_all_games(db: Session, player_id: int) -> List[PlayerGameMetadata]:
    roster_entries = db.query(GameInRoster).join(Game).filter(
        GameInRoster.player_id == player_id
    ).order_by(desc(Game.date)).all()
    return [
        PlayerGameMetadata(
            game_id=r.game.id,
            date=str(r.game.date),
            opponent=r.game.opponent,
            home=r.game.home
        ) for r in roster_entries
    ]

def get_player_tags(db: Session, player_id: int):
    shooter_tags = db.query(PlayerStatsTag).filter(PlayerStatsTag.shooter_id == player_id).all()
    on_ice_tag_ids = db.query(PlayerStatsTagOnIce.tag_id).filter(PlayerStatsTagOnIce.player_id == player_id).all()
    on_ice_tag_ids = [t[0] for t in on_ice_tag_ids]
    on_ice_tags = db.query(PlayerStatsTag).filter(PlayerStatsTag.id.in_(on_ice_tag_ids)).all() if on_ice_tag_ids else []
    participating_tag_ids = db.query(PlayerStatsTagParticipating.tag_id).filter(PlayerStatsTagParticipating.player_id == player_id).all()
    participating_tag_ids = [t[0] for t in participating_tag_ids]
    participating_tags = db.query(PlayerStatsTag).filter(PlayerStatsTag.id.in_(participating_tag_ids)).all() if participating_tag_ids else []
    return shooter_tags, on_ice_tags, participating_tags

def calculate_summary_kpis(games_played: int, shooter_tags: List[PlayerStatsTag], on_ice_tags: List[PlayerStatsTag], participating_tags: List[PlayerStatsTag]) -> SeasonSummaryKPIs:
    summary = SeasonSummaryKPIs(games_played=games_played)
    for tag in shooter_tags:
        result = tag.shot_result.value
        if result == ShotResultTypes.GOAL_FOR:
            summary.goals += 1
            summary.chances += 1
        elif result == ShotResultTypes.CHANCE_FOR:
            summary.chances += 1
    summary.efficiency = round((summary.goals / summary.chances * 100), 1) if summary.chances > 0 else 0.0
    summary.chances_per_game = round((summary.chances / games_played), 1) if games_played > 0 else 0.0
    for tag in participating_tags:
        result = tag.shot_result.value
        if result == ShotResultTypes.GOAL_FOR:
            summary.participation_m_plus += 1
            summary.participation_mp_plus += 1
        elif result == ShotResultTypes.GOAL_AGAINST:
            summary.participation_m_minus += 1
            summary.participation_mp_minus += 1
        elif result == ShotResultTypes.CHANCE_FOR:
            summary.participation_mp_plus += 1
        elif result == ShotResultTypes.CHANCE_AGAINST:
            summary.participation_mp_minus += 1
    summary.participation_m_diff = summary.participation_m_plus - summary.participation_m_minus
    summary.participation_mp_diff = summary.participation_mp_plus - summary.participation_mp_minus
    for tag in on_ice_tags:
        result = tag.shot_result.value
        if result == ShotResultTypes.GOAL_FOR:
            summary.on_ice_m_plus += 1
            summary.on_ice_mp_plus += 1
        elif result == ShotResultTypes.GOAL_AGAINST:
            summary.on_ice_m_minus += 1
            summary.on_ice_mp_minus += 1
        elif result == ShotResultTypes.CHANCE_FOR:
            summary.on_ice_mp_plus += 1
        elif result == ShotResultTypes.CHANCE_AGAINST:
            summary.on_ice_mp_minus += 1
    summary.on_ice_m_diff = summary.on_ice_m_plus - summary.on_ice_m_minus
    summary.on_ice_mp_diff = summary.on_ice_mp_plus - summary.on_ice_mp_minus
    return summary

def get_zone_names(tag: PlayerStatsTag) -> Tuple[str, str]:
    ice_zone_name = tag.shot_area.value.value if tag.shot_area else "UNKNOWN"
    if ice_zone_name in ["ZONE_2_SIDE", "ZONE_4", "OUTSIDE_FAR", "OUTSIDE_CLOSE"]:
        side = "_LEFT" if tag.ice_x < 50 else "_RIGHT"
        ice_zone_name += side
    net_zone_name = f"{tag.net_height}-{tag.net_width}"
    return ice_zone_name, net_zone_name

def calculate_map_stats(player_id: int, shooter_tags: List[PlayerStatsTag], participating_tags: List[PlayerStatsTag]) -> Tuple[Dict[str, ZoneData], Dict[str, ZoneData], List[MarkerData], List[MarkerData]]:
    ice_zones: Dict[str, ZoneData] = {}
    net_zones: Dict[str, ZoneData] = {}
    ice_markers: List[MarkerData] = []
    net_markers: List[MarkerData] = []
    for tag in shooter_tags:
        result = tag.shot_result.value
        if result not in [ShotResultTypes.GOAL_FOR, ShotResultTypes.CHANCE_FOR]:
            continue
        ice_markers.append(MarkerData(x=tag.ice_x, y=tag.ice_y, result=result.value))
        net_markers.append(MarkerData(x=tag.net_x, y=tag.net_y, result=result.value))
        ice_zone_name, net_zone_name = get_zone_names(tag)
        if ice_zone_name not in ice_zones: ice_zones[ice_zone_name] = ZoneData()
        if net_zone_name not in net_zones: net_zones[net_zone_name] = ZoneData()
        if result == ShotResultTypes.GOAL_FOR:
            ice_zones[ice_zone_name].goals_for += 1
            ice_zones[ice_zone_name].chances_for += 1
            net_zones[net_zone_name].goals_for += 1
            net_zones[net_zone_name].chances_for += 1
        elif result == ShotResultTypes.CHANCE_FOR:
            ice_zones[ice_zone_name].chances_for += 1
            net_zones[net_zone_name].chances_for += 1
    return ice_zones, net_zones, ice_markers, net_markers

def calculate_shot_type_stats(shooter_tags: List[PlayerStatsTag]) -> List[ShotTypeStats]:
    stats_dict: Dict[str, ShotTypeStats] = {}
    for tag in shooter_tags:
        s_type = tag.shot_type.value.value if tag.shot_type else "UNKNOWN"
        result = tag.shot_result.value
        if s_type not in stats_dict:
            stats_dict[s_type] = ShotTypeStats(shot_type=s_type)
        stat = stats_dict[s_type]
        if result == ShotResultTypes.GOAL_FOR:
            stat.goals += 1
            stat.chances += 1
        elif result == ShotResultTypes.CHANCE_FOR:
            stat.chances += 1
    for stat in stats_dict.values():
        if stat.chances > 0:
            stat.efficiency = round((stat.goals / stat.chances * 100), 1)
    return list(stats_dict.values())

def calculate_trend_data(db: Session, team_id: int, player_id: int, player_position: Positions, all_games: List[PlayerGameMetadata], shooter_tags: List[PlayerStatsTag]) -> List[GameTrendPoint]:
    games_asc = sorted(all_games, key=lambda x: x.date)
    game_ids = [g.game_id for g in games_asc]
    player_game_stats = {g_id: {"goals": 0, "chances": 0} for g_id in game_ids}
    for tag in shooter_tags:
        if tag.game_id in player_game_stats:
            result = tag.shot_result.value
            if result == ShotResultTypes.GOAL_FOR:
                player_game_stats[tag.game_id]["goals"] += 1
                player_game_stats[tag.game_id]["chances"] += 1
            elif result == ShotResultTypes.CHANCE_FOR:
                player_game_stats[tag.game_id]["chances"] += 1
    peers = db.query(Player).filter(Player.team_id == team_id, Player.position == player_position).all()
    peer_ids = [p.id for p in peers]
    roster_entries = db.query(GameInRoster).filter(GameInRoster.game_id.in_(game_ids), GameInRoster.player_id.in_(peer_ids)).all()
    peers_present_per_game = {g_id: 0 for g_id in game_ids}
    for entry in roster_entries:
        peers_present_per_game[entry.game_id] += 1
    peer_tags = db.query(PlayerStatsTag).filter(PlayerStatsTag.game_id.in_(game_ids), PlayerStatsTag.shooter_id.in_(peer_ids)).all()
    peer_game_totals = {g_id: {"goals": 0, "chances": 0} for g_id in game_ids}
    for tag in peer_tags:
        result = tag.shot_result.value
        if result == ShotResultTypes.GOAL_FOR:
            peer_game_totals[tag.game_id]["goals"] += 1
            peer_game_totals[tag.game_id]["chances"] += 1
        elif result == ShotResultTypes.CHANCE_FOR:
            peer_game_totals[tag.game_id]["chances"] += 1
    peer_game_avgs = {}
    for g_id in game_ids:
        count = peers_present_per_game[g_id]
        if count > 0:
            peer_game_avgs[g_id] = {
                "goals": peer_game_totals[g_id]["goals"] / count,
                "chances": peer_game_totals[g_id]["chances"] / count
            }
        else:
            peer_game_avgs[g_id] = {"goals": 0.0, "chances": 0.0}
    result = []
    for i, g in enumerate(games_asc):
        window_indices = list(range(max(0, i-4), i+1))
        window_games = [games_asc[idx] for idx in window_indices]
        rolling_goals = sum(player_game_stats[wg.game_id]["goals"] for wg in window_games) / len(window_games)
        rolling_chances = sum(player_game_stats[wg.game_id]["chances"] for wg in window_games) / len(window_games)
        team_rolling_goals = sum(peer_game_avgs[wg.game_id]["goals"] for wg in window_games) / len(window_games)
        team_rolling_chances = sum(peer_game_avgs[wg.game_id]["chances"] for wg in window_games) / len(window_games)
        result.append(GameTrendPoint(
            game_id=g.game_id, opponent=g.opponent, date=g.date, goals=player_game_stats[g.game_id]["goals"],
            chances=player_game_stats[g.game_id]["chances"], rolling_goals=round(rolling_goals, 2),
            rolling_chances=round(rolling_chances, 2), team_rolling_goals=round(team_rolling_goals, 2),
            team_rolling_chances=round(team_rolling_chances, 2)
        ))
    return result

def calculate_spider_data(
    db: Session,
    team_id: int,
    player_id: int,
    shooter_tags: List[PlayerStatsTag],
    on_ice_tags: List[PlayerStatsTag],
    participating_tags: List[PlayerStatsTag],
    all_games: List[PlayerGameMetadata]
) -> SpiderChartData:
    num_games = len(all_games)
    if num_games == 0:
        return SpiderChartData(kpis=[])

    # 1. Goals per game
    player_goals = sum(1 for t in shooter_tags if t.shot_result.value == ShotResultTypes.GOAL_FOR)
    gpg = player_goals / num_games

    # 2. Chances participating per game
    player_chances_p = sum(1 for t in participating_tags if t.shot_result.value in [ShotResultTypes.GOAL_FOR, ShotResultTypes.CHANCE_FOR])
    cpg = player_chances_p / num_games

    # 3. 5v5 Corsi
    v5v5_for = sum(1 for t in on_ice_tags if t.strengths == "ES" and t.shot_result.value in [ShotResultTypes.GOAL_FOR, ShotResultTypes.CHANCE_FOR])
    v5v5_against = sum(1 for t in on_ice_tags if t.strengths == "ES" and t.shot_result.value in [ShotResultTypes.GOAL_AGAINST, ShotResultTypes.CHANCE_AGAINST])
    total_5v5 = v5v5_for + v5v5_against
    corsi = (v5v5_for / total_5v5 * 100) if total_5v5 > 0 else 50.0

    # 4. PP Efficiency (on ice)
    pp_goals = sum(1 for t in on_ice_tags if t.strengths == "PP" and t.shot_result.value == ShotResultTypes.GOAL_FOR)
    pp_chances = sum(1 for t in on_ice_tags if t.strengths == "PP" and t.shot_result.value in [ShotResultTypes.GOAL_FOR, ShotResultTypes.CHANCE_FOR])
    pp_eff = (pp_goals / pp_chances * 100) if pp_chances > 0 else 0.0

    # 5. PK workload
    pk_chances = sum(1 for t in on_ice_tags if t.strengths == "PK" and t.shot_result.value in [ShotResultTypes.GOAL_AGAINST, ShotResultTypes.CHANCE_AGAINST])
    pk_workload = pk_chances / num_games

    # Calculate Team Averages
    all_team_players = db.query(Player).filter(Player.team_id == team_id, Player.position != Positions.GOALIE).all()
    player_ids = [p.id for p in all_team_players]
    team_roster_count = db.query(func.count(GameInRoster.game_id)).filter(GameInRoster.player_id.in_(player_ids)).scalar() or 1
    team_shooter_tags = db.query(PlayerStatsTag).filter(PlayerStatsTag.shooter_id.in_(player_ids)).all()
    team_goals = sum(1 for t in team_shooter_tags if t.shot_result.value == ShotResultTypes.GOAL_FOR)
    team_gpg = team_goals / team_roster_count

    team_participating_count = db.query(func.count(PlayerStatsTagParticipating.player_id)).select_from(PlayerStatsTagParticipating).join(PlayerStatsTag).filter(
        PlayerStatsTagParticipating.player_id.in_(player_ids),
        PlayerStatsTag.shot_result_id.in_(
            db.query(ShotResult.id).filter(ShotResult.value.in_([ShotResultTypes.GOAL_FOR, ShotResultTypes.CHANCE_FOR]))
        )
    ).scalar() or 0
    team_cpg = team_participating_count / team_roster_count

    team_on_ice_metrics = db.query(
        PlayerStatsTag.strengths,
        ShotResult.value,
        func.count(PlayerStatsTagOnIce.player_id)
    ).select_from(PlayerStatsTagOnIce).join(PlayerStatsTag).join(ShotResult).filter(
        PlayerStatsTagOnIce.player_id.in_(player_ids)
    ).group_by(PlayerStatsTag.strengths, ShotResult.value).all()

    stats = {}
    for s, r, count in team_on_ice_metrics:
        stats[(s, r)] = count

    team_v5v5_for = stats.get(("ES", ShotResultTypes.GOAL_FOR), 0) + stats.get(("ES", ShotResultTypes.CHANCE_FOR), 0)
    team_v5v5_against = stats.get(("ES", ShotResultTypes.GOAL_AGAINST), 0) + stats.get(("ES", ShotResultTypes.CHANCE_AGAINST), 0)
    team_corsi = (team_v5v5_for / (team_v5v5_for + team_v5v5_against) * 100) if (team_v5v5_for + team_v5v5_against) > 0 else 50.0
    team_pp_goals = stats.get(("PP", ShotResultTypes.GOAL_FOR), 0)
    team_pp_chances = team_pp_goals + stats.get(("PP", ShotResultTypes.CHANCE_FOR), 0)
    team_pp_eff = (team_pp_goals / team_pp_chances * 100) if team_pp_chances > 0 else 0.0
    team_pk_against = stats.get(("PK", ShotResultTypes.GOAL_AGAINST), 0) + stats.get(("PK", ShotResultTypes.CHANCE_AGAINST), 0)
    team_pk_workload = team_pk_against / team_roster_count

    return SpiderChartData(kpis=[
        SpiderChartKPI(label="Maalit / peli", player_value=round(gpg, 2), team_avg=round(team_gpg, 2)),
        SpiderChartKPI(label="Osallisuudet / peli", player_value=round(cpg, 2), team_avg=round(team_cpg, 2)),
        SpiderChartKPI(label="5v5 Corsi %", player_value=round(corsi, 1), team_avg=round(team_corsi, 1)),
        SpiderChartKPI(label="YV Tehokkuus %", player_value=round(pp_eff, 1), team_avg=round(team_pp_eff, 1)),
        SpiderChartKPI(label="AV Työkuorma", player_value=round(pk_workload, 2), team_avg=round(team_pk_workload, 2)),
    ])

def calculate_team_averages(db: Session, team_id: int, player_position: Positions) -> Tuple[float, float]:
    peers = db.query(Player).filter(Player.team_id == team_id, Player.position == player_position).all()
    peer_ids = [p.id for p in peers]
    if not peer_ids: return 0.0, 0.0
    total_peer_games = db.query(func.count(GameInRoster.game_id)).filter(GameInRoster.player_id.in_(peer_ids)).scalar() or 0
    if total_peer_games == 0: return 0.0, 0.0
    shooter_tags = db.query(PlayerStatsTag).filter(PlayerStatsTag.shooter_id.in_(peer_ids)).all()
    total_goals = total_chances = 0
    for tag in shooter_tags:
        if tag.shot_result.value == ShotResultTypes.GOAL_FOR: total_goals += 1; total_chances += 1
        elif tag.shot_result.value == ShotResultTypes.CHANCE_FOR: total_chances += 1
    return round(total_goals / total_peer_games, 2), round(total_chances / total_peer_games, 2)

def build_all_player_tags(shooter_tags: List[PlayerStatsTag], on_ice_tags: List[PlayerStatsTag], participating_tags: List[PlayerStatsTag]) -> List[PlayerTagData]:
    shooter_ids = {t.id for t in shooter_tags}
    on_ice_ids = {t.id for t in on_ice_tags}
    participating_ids = {t.id for t in participating_tags}
    unique_tags: Dict[int, PlayerStatsTag] = {}
    for t in shooter_tags: unique_tags[t.id] = t
    for t in on_ice_tags: unique_tags[t.id] = t
    for t in participating_tags: unique_tags[t.id] = t
    result = []
    for tag_id, tag in unique_tags.items():
        game = tag.game
        ice_zone, net_zone = get_zone_names(tag)
        result.append(PlayerTagData(
            id=tag.id, game_id=game.id, date=str(game.date), opponent=game.opponent, home=game.home, strengths=tag.strengths or "ES",
            ice_x=tag.ice_x, ice_y=tag.ice_y, ice_zone=ice_zone, net_x=tag.net_x, net_y=tag.net_y, net_zone=net_zone,
            net_height=tag.net_height, net_width=tag.net_width, shot_result=tag.shot_result.value.value,
            shot_type=tag.shot_type.value.value if tag.shot_type else "UNKNOWN",
            is_shooter=(tag.id in shooter_ids), is_participating=(tag.id in participating_ids), is_on_ice=(tag.id in on_ice_ids)
        ))
    result.sort(key=lambda x: x.date, reverse=True)
    return result

@router.get("/{player_id}/stats", response_model=PlayerStatsResponse)
def get_player_stats(player_id: int, db: Session = Depends(get_db_session), user_and_team: tuple[User, Team] = Depends(get_current_user_and_team)):
    _, team = user_and_team
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player: raise HTTPException(status_code=404, detail="Player not found")
    if player.team_id != team.id: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this player's statistics.")
    all_games = get_player_all_games(db, player_id)
    shooter_tags, on_ice_tags, participating_tags = get_player_tags(db, player_id)
    summary = calculate_summary_kpis(len(all_games), shooter_tags, on_ice_tags, participating_tags)
    ice_zones, net_zones, ice_markers, net_markers = calculate_map_stats(player_id, shooter_tags, participating_tags)
    all_tags = build_all_player_tags(shooter_tags, on_ice_tags, participating_tags)
    shot_type_stats = calculate_shot_type_stats(shooter_tags)
    trend_data = calculate_trend_data(db, team.id, player.id, player.position, all_games, shooter_tags)
    team_avg_goals, team_avg_chances = calculate_team_averages(db, team.id, player.position)
    spider_data = calculate_spider_data(db, team.id, player.id, shooter_tags, on_ice_tags, participating_tags, all_games)
    return PlayerStatsResponse(
        player_id=player.id, first_name=player.first_name, last_name=player.last_name, jersey_number=player.jersey_number,
        position=player.position.name, team_name=player.team.name if player.team else "No Team",
        summary=summary, ice_zones=ice_zones, net_zones=net_zones, ice_markers=ice_markers, net_markers=net_markers,
        all_tags=all_tags, all_games=all_games, shot_type_stats=shot_type_stats, trend_data=trend_data,
        team_avg_goals=team_avg_goals, team_avg_chances=team_avg_chances, spider_data=spider_data
    )
