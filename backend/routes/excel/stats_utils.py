from enum import Enum
from typing import TypeAlias
from collections import defaultdict
from db.models import ShotResultTypes, Team, Game

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


def get_selected_games(team: Team, game_ids_str: str | None) -> list[Game]:
    if not game_ids_str:
        return team.games

    selected_ids = [int(game_id) for game_id in game_ids_str.split(",")]
    return [game for game in team.games if game.id in selected_ids]
