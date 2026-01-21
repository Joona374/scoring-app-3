# routes/dashboard.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from db.db_manager import get_db_session
from db.models import (
    User, Game, Player, PlayerStatsTag, PlayerStatsTagOnIce, 
    PlayerStatsTagParticipating, ShotResultTypes, GameInRoster
)
from db.pydantic_schemas import ZoneData, GamePlayerStats, GameKPI, DashboardResponse
from utils import get_current_user_id

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def calculate_game_kpi(game: Game, tags: list[PlayerStatsTag], db: Session) -> GameKPI:
    """Calculate KPIs for a single game from its tags, including per-player stats.

    This function now also computes per-situation aggregates and returns them in the
    `situations` field of the returned GameKPI. Situations keys are: 'yht' (total),
    '5v5' (ES), 'YV' (PP), 'AV' (PK).
    """

    # Prepare roster and on-ice/participating lookups once (used by all situation aggregations)
    roster_entries = db.query(GameInRoster).filter(GameInRoster.game_id == game.id).all()
    player_ids_in_game = [r.player_id for r in roster_entries]
    players_in_game = db.query(Player).filter(Player.id.in_(player_ids_in_game)).all()

    tag_ids = [t.id for t in tags]
    on_ice_records = db.query(PlayerStatsTagOnIce).filter(
        PlayerStatsTagOnIce.tag_id.in_(tag_ids)
    ).all() if tag_ids else []
    participating_records = db.query(PlayerStatsTagParticipating).filter(
        PlayerStatsTagParticipating.tag_id.in_(tag_ids)
    ).all() if tag_ids else []

    on_ice_by_tag = {}
    for rec in on_ice_records:
        on_ice_by_tag.setdefault(rec.tag_id, set()).add(rec.player_id)

    participating_by_tag = {}
    for rec in participating_records:
        participating_by_tag.setdefault(rec.tag_id, set()).add(rec.player_id)

    def build_kpi_from_tags(tag_list: list[PlayerStatsTag]):
        # basic counts
        gf = sum(1 for t in tag_list if t.shot_result.value == ShotResultTypes.GOAL_FOR)
        ga = sum(1 for t in tag_list if t.shot_result.value == ShotResultTypes.GOAL_AGAINST)
        cf = sum(1 for t in tag_list if t.shot_result.value in (ShotResultTypes.CHANCE_FOR, ShotResultTypes.GOAL_FOR))
        ca = sum(1 for t in tag_list if t.shot_result.value in (ShotResultTypes.CHANCE_AGAINST, ShotResultTypes.GOAL_AGAINST))

        eff_f = round((gf / cf * 100), 1) if cf > 0 else 0.0
        eff_a = round((ga / ca * 100), 1) if ca > 0 else 0.0

        ice_z: dict[str, ZoneData] = {}
        net_z: dict[str, ZoneData] = {}

        for tag in tag_list:
            result = tag.shot_result.value
            ice_zone_name = tag.shot_area.value.value if tag.shot_area else "UNKNOWN"
            # Split mirrored zones by side based on ice_x coordinate
            if ice_zone_name in ["ZONE_2_SIDE", "ZONE_4", "OUTSIDE_FAR", "OUTSIDE_CLOSE"]:
                if tag.ice_x is not None:
                    side = "_LEFT" if tag.ice_x < 50 else "_RIGHT"
                else:
                    side = "_LEFT"  # default to left if no ice_x
                ice_zone_name += side

            net_zone_name = f"{tag.net_height}-{tag.net_width}"

            if ice_zone_name not in ice_z:
                ice_z[ice_zone_name] = ZoneData()
            if net_zone_name not in net_z:
                net_z[net_zone_name] = ZoneData()

            if result == ShotResultTypes.GOAL_FOR:
                ice_z[ice_zone_name].goals_for += 1
                ice_z[ice_zone_name].chances_for += 1
                net_z[net_zone_name].goals_for += 1
                net_z[net_zone_name].chances_for += 1
            elif result == ShotResultTypes.GOAL_AGAINST:
                ice_z[ice_zone_name].goals_against += 1
                ice_z[ice_zone_name].chances_against += 1
                net_z[net_zone_name].goals_against += 1
                net_z[net_zone_name].chances_against += 1
            elif result == ShotResultTypes.CHANCE_FOR:
                ice_z[ice_zone_name].chances_for += 1
                net_z[net_zone_name].chances_for += 1
            elif result == ShotResultTypes.CHANCE_AGAINST:
                ice_z[ice_zone_name].chances_against += 1
                net_z[net_zone_name].chances_against += 1

        # per-player stats for this tag subset
        player_stats_local: list[GamePlayerStats] = []
        for player in players_in_game:
            stats = GamePlayerStats(
                player_id=player.id,
                first_name=player.first_name,
                last_name=player.last_name,
                jersey_number=player.jersey_number,
            )

            for tag in tag_list:
                result = tag.shot_result.value
                is_shooter = tag.shooter_id == player.id
                is_on_ice = player.id in on_ice_by_tag.get(tag.id, set())
                is_participating = player.id in participating_by_tag.get(tag.id, set())

                if is_shooter:
                    if result == ShotResultTypes.GOAL_FOR:
                        stats.goals += 1
                        stats.chances += 1
                    elif result == ShotResultTypes.CHANCE_FOR:
                        stats.chances += 1

                if is_on_ice:
                    if result == ShotResultTypes.GOAL_FOR:
                        stats.goals_plus_on_ice += 1
                        stats.chances_plus_on_ice += 1
                    elif result == ShotResultTypes.GOAL_AGAINST:
                        stats.goals_minus_on_ice += 1
                        stats.chances_minus_on_ice += 1
                    elif result == ShotResultTypes.CHANCE_FOR:
                        stats.chances_plus_on_ice += 1
                    elif result == ShotResultTypes.CHANCE_AGAINST:
                        stats.chances_minus_on_ice += 1

                if is_participating:
                    if result == ShotResultTypes.GOAL_FOR:
                        stats.goals_plus_participating += 1
                        stats.chances_plus_participating += 1
                    elif result == ShotResultTypes.GOAL_AGAINST:
                        stats.goals_minus_participating += 1
                        stats.chances_minus_participating += 1
                    elif result == ShotResultTypes.CHANCE_FOR:
                        stats.chances_plus_participating += 1
                    elif result == ShotResultTypes.CHANCE_AGAINST:
                        stats.chances_minus_participating += 1

            player_stats_local.append(stats)

        return {
            "goals_for": gf,
            "goals_against": ga,
            "chances_for": cf,
            "chances_against": ca,
            "efficiency_for": eff_f,
            "efficiency_against": eff_a,
            "ice_zones": ice_z,
            "net_zones": net_z,
            "player_stats": player_stats_local,
        }

    # Build situation-specific tag lists
    situations = {}
    # Total (yht) includes all tags (including EN+/EN-)
    situations["yht"] = build_kpi_from_tags(tags)
    # 5v5 -> strengths == 'ES'
    situations["5v5"] = build_kpi_from_tags([t for t in tags if getattr(t, "strengths", None) == "ES"]) if tags else build_kpi_from_tags([])
    # YV (powerplay) -> strengths == 'PP'
    situations["YV"] = build_kpi_from_tags([t for t in tags if getattr(t, "strengths", None) == "PP"]) if tags else build_kpi_from_tags([])
    # AV (penaltykill) -> strengths == 'PK'
    situations["AV"] = build_kpi_from_tags([t for t in tags if getattr(t, "strengths", None) == "PK"]) if tags else build_kpi_from_tags([])

    # Use the total (yht) as the top-level KPI for backward compatibility
    total_kpi = situations["yht"]

    return GameKPI(
        game_id=game.id,
        date=str(game.date),
        opponent=game.opponent,
        home=game.home,
        goals_for=total_kpi["goals_for"],
        goals_against=total_kpi["goals_against"],
        chances_for=total_kpi["chances_for"],
        chances_against=total_kpi["chances_against"],
        efficiency_for=total_kpi["efficiency_for"],
        efficiency_against=total_kpi["efficiency_against"],
        ice_zones=total_kpi["ice_zones"],
        net_zones=total_kpi["net_zones"],
        player_stats=total_kpi["player_stats"],
        situations=situations,
    )


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """Get dashboard summary data for the current user's team."""
    
    # Get user and team
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.team:
        raise HTTPException(status_code=404, detail="User has no team")
    
    team = user.team
    
    # Get ALL games ordered by date descending (newest first)
    all_games = db.query(Game).filter(
        Game.team_id == team.id
    ).order_by(desc(Game.date)).all()
    
    all_game_ids = [g.id for g in all_games]
    
    # Get all tags for ALL games
    all_season_tags = db.query(PlayerStatsTag).filter(
        PlayerStatsTag.game_id.in_(all_game_ids)
    ).all() if all_game_ids else []
    
    # Calculate KPI for each game (includes zone stats and player stats per game)
    game_kpis: list[GameKPI] = []
    for game in all_games:
        game_tags = [t for t in all_season_tags if t.game_id == game.id]
        kpi = calculate_game_kpi(game, game_tags, db)
        game_kpis.append(kpi)
    
    return DashboardResponse(
        team_name=team.name,
        games=game_kpis,
    )
