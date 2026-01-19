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
    """Calculate KPIs for a single game from its tags, including per-player stats."""
    goals_for = sum(1 for t in tags if t.shot_result.value == ShotResultTypes.GOAL_FOR)
    goals_against = sum(1 for t in tags if t.shot_result.value == ShotResultTypes.GOAL_AGAINST)
    chances_for = sum(1 for t in tags if t.shot_result.value in (ShotResultTypes.CHANCE_FOR, ShotResultTypes.GOAL_FOR))
    chances_against = sum(1 for t in tags if t.shot_result.value in (ShotResultTypes.CHANCE_AGAINST, ShotResultTypes.GOAL_AGAINST))

    efficiency_for = round((goals_for / chances_for * 100), 1) if chances_for > 0 else 0.0
    efficiency_against = round((goals_against / chances_against * 100), 1) if chances_against > 0 else 0.0

    # Calculate zone stats for this game
    ice_zones: dict[str, ZoneData] = {}
    net_zones: dict[str, ZoneData] = {}

    for tag in tags:
        result = tag.shot_result.value
        ice_zone_name = tag.shot_area.value.value if tag.shot_area else "UNKNOWN"
        net_zone_name = f"{tag.net_height}-{tag.net_width}"

        # Initialize zones if needed
        if ice_zone_name not in ice_zones:
            ice_zones[ice_zone_name] = ZoneData()
        if net_zone_name not in net_zones:
            net_zones[net_zone_name] = ZoneData()

        # Update counts based on result type
        if result == ShotResultTypes.GOAL_FOR:
            ice_zones[ice_zone_name].goals_for += 1
            ice_zones[ice_zone_name].chances_for += 1
            net_zones[net_zone_name].goals_for += 1
            net_zones[net_zone_name].chances_for += 1
        elif result == ShotResultTypes.GOAL_AGAINST:
            ice_zones[ice_zone_name].goals_against += 1
            ice_zones[ice_zone_name].chances_against += 1
            net_zones[net_zone_name].goals_against += 1
            net_zones[net_zone_name].chances_against += 1
        elif result == ShotResultTypes.CHANCE_FOR:
            ice_zones[ice_zone_name].chances_for += 1
            net_zones[net_zone_name].chances_for += 1
        elif result == ShotResultTypes.CHANCE_AGAINST:
            ice_zones[ice_zone_name].chances_against += 1
            net_zones[net_zone_name].chances_against += 1

    # Calculate per-player stats for this game
    # Get players in this game's roster
    roster_entries = db.query(GameInRoster).filter(GameInRoster.game_id == game.id).all()
    player_ids_in_game = [r.player_id for r in roster_entries]
    players_in_game = db.query(Player).filter(Player.id.in_(player_ids_in_game)).all()

    # Get on-ice and participating records for tags in this game
    tag_ids = [t.id for t in tags]
    on_ice_records = db.query(PlayerStatsTagOnIce).filter(
        PlayerStatsTagOnIce.tag_id.in_(tag_ids)
    ).all() if tag_ids else []
    participating_records = db.query(PlayerStatsTagParticipating).filter(
        PlayerStatsTagParticipating.tag_id.in_(tag_ids)
    ).all() if tag_ids else []

    # Build lookup sets: tag_id -> set of player_ids
    on_ice_by_tag = {}
    for rec in on_ice_records:
        on_ice_by_tag.setdefault(rec.tag_id, set()).add(rec.player_id)

    participating_by_tag = {}
    for rec in participating_records:
        participating_by_tag.setdefault(rec.tag_id, set()).add(rec.player_id)

    # Calculate stats for each player
    player_stats_list: list[GamePlayerStats] = []

    for player in players_in_game:
        stats = GamePlayerStats(
            player_id=player.id,
            first_name=player.first_name,
            last_name=player.last_name,
            jersey_number=player.jersey_number,
        )

        for tag in tags:
            result = tag.shot_result.value
            is_shooter = tag.shooter_id == player.id
            is_on_ice = player.id in on_ice_by_tag.get(tag.id, set())
            is_participating = player.id in participating_by_tag.get(tag.id, set())

            # Personal goals and chances (as shooter)
            if is_shooter:
                if result == ShotResultTypes.GOAL_FOR:
                    stats.goals += 1
                    stats.chances += 1
                elif result == ShotResultTypes.CHANCE_FOR:
                    stats.chances += 1

            # On-ice +/-
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

            # Participating +/-
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

        player_stats_list.append(stats)

    return GameKPI(
        game_id=game.id,
        date=str(game.date),
        opponent=game.opponent,
        home=game.home,
        goals_for=goals_for,
        goals_against=goals_against,
        chances_for=chances_for,
        chances_against=chances_against,
        efficiency_for=efficiency_for,
        efficiency_against=efficiency_against,
        ice_zones=ice_zones,
        net_zones=net_zones,
        player_stats=player_stats_list,
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
