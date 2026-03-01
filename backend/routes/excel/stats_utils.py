from enum import Enum
from typing import TypeAlias
from collections import defaultdict
from db.models import ShotResultTypes, Team, Game
from sqlalchemy.orm import Session


class MapCategories(str, Enum):
    ICE = "ice"
    NET = "net"

Point: TypeAlias = tuple[int, int]
CategoryMap: TypeAlias = defaultdict[MapCategories, list[Point]]
ResultMap: TypeAlias = dict[ShotResultTypes, CategoryMap]

MAP_RESULT_MAPPING: dict[ShotResultTypes, list[ShotResultTypes]] = {
    ShotResultTypes.CHANCE_FOR: [ShotResultTypes.CHANCE_FOR],
    ShotResultTypes.GOAL_FOR: [ShotResultTypes.CHANCE_FOR, ShotResultTypes.GOAL_FOR],
    ShotResultTypes.CHANCE_AGAINST: [ShotResultTypes.CHANCE_AGAINST],
    ShotResultTypes.GOAL_AGAINST: [ShotResultTypes.CHANCE_AGAINST, ShotResultTypes.GOAL_AGAINST],
}

STATS_CELL_VALUES = "cell_values"
STATS_MAP_COORDINATES = "coordinates"
STATS_PER_GAME_STATS = "per_game_stats"
STATS_SHOOTER_TAGS = "shooter_tags"
STATS_ON_ICE_STATS = "on_ice_tags"

MAPPED_DATA_FOR = "for"
MAPPED_DATA_AGAINST = "against"


def get_selected_games(game_ids_str: str | None, team: Team, db: Session) -> list[Game]:
    """
    Get a list of selected games for a team based on provided game IDs.

    Args:
        game_ids_str (str | None): Comma-separated string of game IDs, or None for all games.
        team (Team): The users team object to validate permission to access these games.
        db: (session): db handle to query for games

    Returns:
        list[Game]: List of selected games as Game objects.
    """

    db_query = db.query(Game).filter(Game.team_id == team.id)

    if game_ids_str:
        selected_ids = [int(game_id) for game_id in game_ids_str.split(",")]
        db_query = db_query.filter(Game.id.in_(selected_ids))

    games = db_query.all()
    return games
