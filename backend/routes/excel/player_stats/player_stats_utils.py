from typing import TypedDict
from db.models import ShotAreaTypes

class PlayerStats(TypedDict):
    games: int
    first_name: str
    last_name: str
    shooter_tags: list
    on_ice_tags: list
    cell_values: dict
    per_game_stats: list
    coordinates: dict

ZONE_COLUMN_MAPPING = {
    ShotAreaTypes.ZONE_1: "B",
    ShotAreaTypes.ZONE_2_MIDDLE: "D",
    ShotAreaTypes.ZONE_2_SIDE: "F",
    ShotAreaTypes.HIGH_SLOT: "H",
    ShotAreaTypes.BLUELINE: "J",
    ShotAreaTypes.ZONE_4: "L",
    ShotAreaTypes.OUTSIDE_FAR: "N",
    ShotAreaTypes.OUTSIDE_CLOSE: "P",
    ShotAreaTypes.MISC: "R",
}
