from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.db_manager import get_db_session
from db.models import (
    Player, Team, PlayerStatsTag, PlayerStatsTagOnIce, 
    PlayerStatsTagParticipating, ShotResultTypes, GameInRoster, User
)
from db.pydantic_schemas import PlayerStatsResponse, SeasonSummaryKPIs, ZoneData, MarkerData
from utils import get_current_user_and_team

router = APIRouter()

def get_player_games_played(db: Session, player_id: int) -> int:
    return db.query(func.count(GameInRoster.game_id)).filter(GameInRoster.player_id == player_id).scalar() or 0

def get_player_tags(db: Session, player_id: int):
    # 1. Shooter tags
    shooter_tags = db.query(PlayerStatsTag).filter(
        PlayerStatsTag.shooter_id == player_id
    ).all()

    # 2. On-ice tags
    on_ice_tag_ids = db.query(PlayerStatsTagOnIce.tag_id).filter(
        PlayerStatsTagOnIce.player_id == player_id
    ).all()
    on_ice_tag_ids = [t[0] for t in on_ice_tag_ids]
    on_ice_tags = db.query(PlayerStatsTag).filter(
        PlayerStatsTag.id.in_(on_ice_tag_ids)
    ).all() if on_ice_tag_ids else []

    # 3. Participating tags
    participating_tag_ids = db.query(PlayerStatsTagParticipating.tag_id).filter(
        PlayerStatsTagParticipating.player_id == player_id
    ).all()
    participating_tag_ids = [t[0] for t in participating_tag_ids]
    participating_tags = db.query(PlayerStatsTag).filter(
        PlayerStatsTag.id.in_(participating_tag_ids)
    ).all() if participating_tag_ids else []

    return shooter_tags, on_ice_tags, participating_tags


def calculate_summary_kpis(games_played: int, shooter_tags: list[PlayerStatsTag], on_ice_tags: list[PlayerStatsTag], participating_tags: list[PlayerStatsTag]) -> SeasonSummaryKPIs:
    summary = SeasonSummaryKPIs(games_played=games_played)

    # Goals and Chances (Shooter)
    for tag in shooter_tags:
        result = tag.shot_result.value
        if result == ShotResultTypes.GOAL_FOR:
            summary.goals += 1
            summary.chances += 1
        elif result == ShotResultTypes.CHANCE_FOR:
            summary.chances += 1

    summary.efficiency = round((summary.goals / summary.chances * 100), 1) if summary.chances > 0 else 0.0
    summary.chances_per_game = round((summary.chances / games_played), 1) if games_played > 0 else 0.0

    # Participation Stats
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

    # On-Ice Stats
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


def calculate_map_stats(shooter_tags: list[PlayerStatsTag]) -> tuple[dict[str, ZoneData], dict[str, ZoneData], list[MarkerData], list[MarkerData]]:
    ice_zones: dict[str, ZoneData] = {}
    net_zones: dict[str, ZoneData] = {}
    ice_markers: list[MarkerData] = []
    net_markers: list[MarkerData] = []

    for tag in shooter_tags:
        result = tag.shot_result.value
        ice_x, ice_y = tag.ice_x, tag.ice_y
        net_x, net_y = tag.net_x, tag.net_y

        # Only process positive results for the player's own maps
        if result not in [ShotResultTypes.GOAL_FOR, ShotResultTypes.CHANCE_FOR]:
            continue

        # Ice markers
        ice_markers.append(MarkerData(x=ice_x, y=ice_y, result=result.value))

        # Net markers
        net_markers.append(MarkerData(x=net_x, y=net_y, result=result.value))

        # Zone Stats
        ice_zone_name = tag.shot_area.value.value if tag.shot_area else "UNKNOWN"
        if ice_zone_name in ["ZONE_2_SIDE", "ZONE_4", "OUTSIDE_FAR", "OUTSIDE_CLOSE"]:
            side = "_LEFT" if ice_x < 50 else "_RIGHT"
            ice_zone_name += side

        net_zone_name = f"{tag.net_height}-{tag.net_width}"

        if ice_zone_name not in ice_zones:
            ice_zones[ice_zone_name] = ZoneData()
        if net_zone_name not in net_zones:
            net_zones[net_zone_name] = ZoneData()

        if result == ShotResultTypes.GOAL_FOR:
            ice_zones[ice_zone_name].goals_for += 1
            ice_zones[ice_zone_name].chances_for += 1
            net_zones[net_zone_name].goals_for += 1
            net_zones[net_zone_name].chances_for += 1
        elif result == ShotResultTypes.CHANCE_FOR:
            ice_zones[ice_zone_name].chances_for += 1
            net_zones[net_zone_name].chances_for += 1

    return ice_zones, net_zones, ice_markers, net_markers


@router.get("/{player_id}/stats", response_model=PlayerStatsResponse)
def get_player_stats(
    player_id: int,
    db: Session = Depends(get_db_session),
    user_and_team: tuple[User, Team] = Depends(get_current_user_and_team)
):
    """Get detailed statistics for a single player."""
    _, team = user_and_team

    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    if player.team_id != team.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this player's statistics.")

    games_played = get_player_games_played(db, player_id)
    shooter_tags, on_ice_tags, participating_tags = get_player_tags(db, player_id)

    summary = calculate_summary_kpis(games_played, shooter_tags, on_ice_tags, participating_tags)
    ice_zones, net_zones, ice_markers, net_markers = calculate_map_stats(
        shooter_tags,
    )

    return PlayerStatsResponse(
        player_id=player.id,
        first_name=player.first_name,
        last_name=player.last_name,
        jersey_number=player.jersey_number,
        position=player.position.name,
        team_name=player.team.name if player.team else "No Team",
        summary=summary,
        ice_zones=ice_zones,
        net_zones=net_zones,
        ice_markers=ice_markers,
        net_markers=net_markers,
    )
