from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from db.db_manager import get_db_session
from db.models import (
    Player, Team, PlayerStatsTag, PlayerStatsTagOnIce, 
    PlayerStatsTagParticipating, ShotResultTypes, GameInRoster, User
)
from db.pydantic_schemas import PlayerStatsResponse, SeasonSummaryKPIs
from utils import get_current_user_and_team

router = APIRouter()

def get_player_games_played(db: Session, player_id: int) -> int:
    return db.query(GameInRoster).filter(GameInRoster.player_id == player_id).count()

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

def calculate_summary_kpis(
    games_played: int, 
    shooter_tags: List[PlayerStatsTag], 
    on_ice_tags: List[PlayerStatsTag], 
    participating_tags: List[PlayerStatsTag]
) -> SeasonSummaryKPIs:
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

def validate_player_belongs_to_team(player: "Player", team: "Team"):
    """Validate that the player belongs to the user's team. If not, raise a 403 Forbidden error."""
    if player.team_id != team.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this player's statistics.")

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
    
    validate_player_belongs_to_team(player, team)
    
    games_played = get_player_games_played(db, player_id)
    shooter_tags, on_ice_tags, participating_tags = get_player_tags(db, player_id)
    summary = calculate_summary_kpis(games_played, shooter_tags, on_ice_tags, participating_tags)
    
    return PlayerStatsResponse(
        player_id=player.id,
        first_name=player.first_name,
        last_name=player.last_name,
        jersey_number=player.jersey_number,
        position=player.position.name,
        team_name=player.team.name if player.team else "No Team",
        summary=summary
    )
