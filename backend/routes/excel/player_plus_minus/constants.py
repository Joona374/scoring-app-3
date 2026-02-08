from typing import TypedDict
from db.models import ShotResultTypes
from datetime import date as datetime_date


SHOTRESULT_TO_CODE_MAP = {
    ShotResultTypes.GOAL_FOR: "G+",
    ShotResultTypes.GOAL_AGAINST: "G-",
    ShotResultTypes.CHANCE_FOR: "C+",
    ShotResultTypes.CHANCE_AGAINST: "C-",
}

FIRST_DEFENDER_ROW = 4
FIRST_FORWARD_ROW = 26

RESULT_TO_COLUMN_MAP = {
    "OIG+": "A",  # OIG+ = On ice Goal +
    "OIG-": "B",  # OIG- = On ice Goal -
    "OIC+": "D",  # OIC+ = On ice Chance +
    "OIC-": "E",  # OIC- = On ice Chance -
    "PG+": "H",  # PG+ = Participated Goal +
    "PG-": "I",  # PG- = Participated Goal -
    "PC+": "K",  # PC+ = Participated chance +
    "PC-": "L",  # PC- = Participated chance -
    "ES-OIG+": "A",  # ES = Even Strength
    "ES-OIG-": "B",
    "ES-OIC+": "D",
    "ES-OIC-": "E",
    "ES-PG+": "H",
    "ES-PG-": "I",
    "ES-PC+": "K",
    "ES-PC-": "L",
    "PP-OIG+": "O",  # PP = Powerplay
    "PP-OIG-": "P",
    "PP-OIC+": "R",
    "PP-OIC-": "S",
    "PP-PG+": "V",
    "PP-PG-": "W",
    "PP-PC+": "Y",
    "PP-PC-": "Z",
    "PK-OIG+": "AC",  # PK = Penaltykill
    "PK-OIG-": "AD",
    "PK-OIC+": "AF",
    "PK-OIC-": "AG",
    "PK-PG+": "AJ",
    "PK-PG-": "AK",
    "PK-PC+": "AM",
    "PK-PC-": "AN",
}

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

class PlayerData(TypedDict):
    name: str
    position: str
    GP: int
    stats: dict[str, int] # This will take the values of STAT_KEYS

class GameDataStructure(TypedDict):
    game_id: int 
    opponent: str 
    home: bool
    date: datetime_date
    roster: dict[int, PlayerData]
    roster_by_positions: dict[str, list[PlayerData]]
