from enum import Enum
from typing import TypedDict

from numpy import empty
from db.models import Positions, ShotResultTypes
from datetime import date as datetime_date


SHOTRESULT_TO_CODE_MAP = {
    ShotResultTypes.GOAL_FOR: "G+",
    ShotResultTypes.GOAL_AGAINST: "G-",
    ShotResultTypes.CHANCE_FOR: "C+",
    ShotResultTypes.CHANCE_AGAINST: "C-",
}

FIRST_DEFENDER_ROW = 4
FIRST_FORWARD_ROW = 26


NAME_COLUMNS = ["G", "U", "AI", "AW"]

# Situation (ES, PP or PK)-Participation or On ice (P/OI)-Outcome (G+, G-, C+, C-)
STAT_KEYS = (
    "ES-PG+",
    "ES-PG-",
    "ES-PC+",
    "ES-PC-",
    "ES-OIG+",
    "ES-OIG-",
    "ES-OIC+",
    "ES-OIC-",
    "PP-PG+",
    "PP-PG-",
    "PP-PC+",
    "PP-PC-",
    "PP-OIG+",
    "PP-OIG-",
    "PP-OIC+",
    "PP-OIC-",
    "PK-PG+",
    "PK-PG-",
    "PK-PC+",
    "PK-PC-",
    "PK-OIG+",
    "PK-OIG-",
    "PK-OIC+",
    "PK-OIC-",
)

EMPTY_STATS = {key: 0 for key in STAT_KEYS}


class ParticipationTypes(Enum):
    ON_ICE = "on_ice"
    PARTICIPATING = "participating"


class StrengthTypes(Enum):
    EVEN_STRENGTH = "ES"
    POWERPLAY = "PP"
    PENALTY_KILL = "PK"


def strenghts_str_to_enum(strength_str: str) -> StrengthTypes:
    strength_mapping = {strength_type.value: strength_type for strength_type in StrengthTypes}
    strength_enum = strength_mapping[strength_str]
    return strength_enum

RESULT_TO_COLUMN_MAP = {
    StrengthTypes.EVEN_STRENGTH: {
        ParticipationTypes.ON_ICE: {
            ShotResultTypes.GOAL_FOR: "A",
            ShotResultTypes.GOAL_AGAINST: "B",
            ShotResultTypes.CHANCE_FOR: "D",
            ShotResultTypes.CHANCE_AGAINST: "E",
        },
        ParticipationTypes.PARTICIPATING: {
            ShotResultTypes.GOAL_FOR: "H",
            ShotResultTypes.GOAL_AGAINST: "I",
            ShotResultTypes.CHANCE_FOR: "K",
            ShotResultTypes.CHANCE_AGAINST: "L",
        },
    },
    StrengthTypes.POWERPLAY: {
        ParticipationTypes.ON_ICE: {
            ShotResultTypes.GOAL_FOR: "O",
            ShotResultTypes.GOAL_AGAINST: "P",
            ShotResultTypes.CHANCE_FOR: "S",
            ShotResultTypes.CHANCE_AGAINST: "R",
        },
        ParticipationTypes.PARTICIPATING: {
            ShotResultTypes.GOAL_FOR: "V",
            ShotResultTypes.GOAL_AGAINST: "W",
            ShotResultTypes.CHANCE_FOR: "Y",
            ShotResultTypes.CHANCE_AGAINST: "Z",
        },
    },
    StrengthTypes.PENALTY_KILL: {
        ParticipationTypes.ON_ICE: {
            ShotResultTypes.GOAL_FOR: "AC",
            ShotResultTypes.GOAL_AGAINST: "AD",
            ShotResultTypes.CHANCE_FOR: "AF",
            ShotResultTypes.CHANCE_AGAINST: "AG",
        },
        ParticipationTypes.PARTICIPATING: {
            ShotResultTypes.GOAL_FOR: "AJ",
            ShotResultTypes.GOAL_AGAINST: "AK",
            ShotResultTypes.CHANCE_FOR: "AM",
            ShotResultTypes.CHANCE_AGAINST: "AN",
        },
    },
}


def build_empty_stats() -> dict:
    """
    Builds an empty statistics dictionary with nested keys for strength, participation type, and shot result, all initialized to 0.
    """

    empty_stats = {}
    for strenght in StrengthTypes:
        empty_stats[strenght] = {}
        for participation_type in ParticipationTypes:
            empty_stats[strenght][participation_type] = {}
            for result in ShotResultTypes:
                empty_stats[strenght][participation_type][result] = 0

    return empty_stats


class PlayerData(TypedDict):
    name: str
    position: Positions
    GP: int
    stats: dict[StrengthTypes, dict[ParticipationTypes, dict[ShotResultTypes, int]]]

class GameDataStructure(TypedDict):
    game_id: int 
    opponent: str 
    home: bool
    date: datetime_date
    roster: dict[int, PlayerData]
    roster_by_positions: dict[Positions, list[PlayerData]]
