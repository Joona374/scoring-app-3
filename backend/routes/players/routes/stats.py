from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Tuple, Set
from db.db_manager import get_db_session
from db.models import (
    Player, Team, PlayerStatsTag, PlayerStatsTagOnIce, 
    PlayerStatsTagParticipating, ShotResultTypes, GameInRoster, User, Game
)
from db.pydantic_schemas import PlayerStatsResponse, SeasonSummaryKPIs, ZoneData, MarkerData, PlayerTagData, PlayerGameMetadata
from utils import get_current_user_and_team

router = APIRouter()

def get_player_all_games(db: Session, player_id: int) -> List[PlayerGameMetadata]:
    # Fetch all games the player was in roster for, ordered by date descending
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
    shooter_tags = db.query(PlayerStatsTag).filter(
        PlayerStatsTag.shooter_id == player_id
    ).all()

    on_ice_tag_ids = db.query(PlayerStatsTagOnIce.tag_id).filter(
        PlayerStatsTagOnIce.player_id == player_id
    ).all()
    on_ice_tag_ids = [t[0] for t in on_ice_tag_ids]
    on_ice_tags = db.query(PlayerStatsTag).filter(
        PlayerStatsTag.id.in_(on_ice_tag_ids)
    ).all() if on_ice_tag_ids else []

    participating_tag_ids = db.query(PlayerStatsTagParticipating.tag_id).filter(
        PlayerStatsTagParticipating.player_id == player_id
    ).all()
    participating_tag_ids = [t[0] for t in participating_tag_ids]
    participating_tags = db.query(PlayerStatsTag).filter(
        PlayerStatsTag.id.in_(participating_tag_ids)
    ).all() if participating_tag_ids else []

    return shooter_tags, on_ice_tags, participating_tags

def calculate_summary_kpis(
    games_played: int, 
    shooter_tags: List[PlayerStatsTag], 
    on_ice_tags: List[PlayerStatsTag], 
    participating_tags: List[PlayerStatsTag]
) -> SeasonSummaryKPIs:
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

def calculate_map_stats(
    player_id: int, 
    shooter_tags: List[PlayerStatsTag], 
    participating_tags: List[PlayerStatsTag]
) -> Tuple[Dict[str, ZoneData], Dict[str, ZoneData], List[MarkerData], List[MarkerData]]:
    ice_zones: Dict[str, ZoneData] = {}
    net_zones: Dict[str, ZoneData] = {}
    ice_markers: List[MarkerData] = []
    net_markers: List[MarkerData] = []

    # Map tags = specifically as shooter (as per Component 3 V2 feedback)
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

def build_all_player_tags(
    shooter_tags: List[PlayerStatsTag], 
    on_ice_tags: List[PlayerStatsTag], 
    participating_tags: List[PlayerStatsTag]
) -> List[PlayerTagData]:
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
            id=tag.id,
            game_id=game.id,
            date=str(game.date),
            opponent=game.opponent,
            home=game.home,
            strengths=tag.strengths or "ES",
            ice_x=tag.ice_x,
            ice_y=tag.ice_y,
            ice_zone=ice_zone,
            net_x=tag.net_x,
            net_y=tag.net_y,
            net_zone=net_zone,
            net_height=tag.net_height,
            net_width=tag.net_width,
            shot_result=tag.shot_result.value.value,
            shot_type=tag.shot_type.value.value if tag.shot_type else "UNKNOWN",
            is_shooter=(tag.id in shooter_ids),
            is_participating=(tag.id in participating_ids),
            is_on_ice=(tag.id in on_ice_ids)
        ))
    
    result.sort(key=lambda x: x.date, reverse=True)
    return result

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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have access to this player's statistics."
        )
    
    all_games = get_player_all_games(db, player_id)
    shooter_tags, on_ice_tags, participating_tags = get_player_tags(db, player_id)
    
    summary = calculate_summary_kpis(len(all_games), shooter_tags, on_ice_tags, participating_tags)
    ice_zones, net_zones, ice_markers, net_markers = calculate_map_stats(player_id, shooter_tags, participating_tags)
    all_tags = build_all_player_tags(shooter_tags, on_ice_tags, participating_tags)
    
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
        all_tags=all_tags,
        all_games=all_games
    )
