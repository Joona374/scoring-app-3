from pydantic import BaseModel
from db.pydantic_schema.shared import ZoneData

class GamePlayerStats(BaseModel):
    """Per-game stats for a single player"""

    player_id: int
    first_name: str
    last_name: str
    jersey_number: int
    goals: int = 0
    chances: int = 0
    goals_plus_on_ice: int = 0
    goals_minus_on_ice: int = 0
    chances_plus_on_ice: int = 0
    chances_minus_on_ice: int = 0
    goals_plus_participating: int = 0
    goals_minus_participating: int = 0
    chances_plus_participating: int = 0
    chances_minus_participating: int = 0


class SituationKPI(BaseModel):
    goals_for: int
    goals_against: int
    chances_for: int
    chances_against: int
    efficiency_for: float
    efficiency_against: float
    ice_zones: dict[str, ZoneData]
    net_zones: dict[str, ZoneData]
    player_stats: list[GamePlayerStats]


class GameKPI(BaseModel):
    game_id: int
    date: str
    opponent: str
    home: bool
    goals_for: int
    goals_against: int
    chances_for: int
    chances_against: int
    efficiency_for: float
    efficiency_against: float
    ice_zones: dict[str, ZoneData]
    net_zones: dict[str, ZoneData]
    player_stats: list[GamePlayerStats]
    situations: dict[str, "SituationKPI"] | None = None


class DashboardResponse(BaseModel):
    team_name: str
    games: list[GameKPI]
