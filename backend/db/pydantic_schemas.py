from pydantic import BaseModel, EmailStr, field_validator
from db.models import Positions
from typing import Optional, List, Dict
from datetime import date

class UserCreate(BaseModel):
    model_config = {"extra": "forbid"}
    email: EmailStr
    username: str
    password: str
    code: str

    @field_validator("username")
    @classmethod
    def no_at_sign_in_username(cls, v):
        if "@" in v:
            raise ValueError("Username cannot contain '@' symbol")
        return v
    
    @field_validator("password")
    @classmethod
    def minimum_password_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password has to be atleast 8 characters")
        return v
    
    @field_validator("code")
    @classmethod
    def code_6_char_len(cls, v):
        if len(v) != 6:
            raise ValueError("Registeration Code must be 6 characters long")
        return v


class UserLogin(BaseModel):
    model_config = {"extra": "forbid"}
    user: str
    password: str

class LoginResponse(BaseModel):
    model_config = {"extra": "forbid"}
    username: str
    user_id: int
    is_admin: bool
    jwt_token: str
    team_id: Optional[int] = None

class UserData(BaseModel):
    model_config = {"extra": "forbid"}
    id: int
    username: str
    email: str

class TeamCreate(BaseModel):
    model_config = {"extra": "forbid"}
    name: str

class TeamCreateResponse(BaseModel):
    team_name:str
    code_for_team: str

class PlayerCreate(BaseModel):
    model_config = {"extra": "forbid"}
    first_name: str
    last_name: str
    jersey_number: int
    position: Positions

class PlayerUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    jersey_number: Optional[int]
    position: Optional[Positions]

class PlayerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    jersey_number: int
    position: str

class TagSchema(BaseModel):
    location: dict
    shot_result: str
    shot_type: str
    extra_data: Optional[str]

class AddTag(BaseModel):
    model_config = {"extra": "forbid"}
    tag: dict

class TeamResponse(BaseModel):
    team_name: str | None
    join_code: str | None
    players: List[PlayerResponse] | None

class PositionInRoster(BaseModel):
    line: int
    position: str
    player: Optional[PlayerResponse]

class GameCreate(BaseModel):
    opponent: str
    game_date: date
    home_game: bool
    players_in_roster: List[PositionInRoster]
    powerplays: Optional[int] = 0
    penalty_kills: Optional[int] = 0

class GameInRosterResponse(BaseModel):
    line: int
    position: str
    player: Optional[PlayerResponse]

class TeamStatsTagResponse(BaseModel):
    id: Optional[int]
    succes: bool
    tag: dict

class PlayerStatsTagResponse(BaseModel):
    id: Optional[int]
    succes: bool

class CreateCode(BaseModel):
    new_code_identifier: str

class CreateCodeResponse(BaseModel):
    code: str
    used: bool
    identifier: str | None
    creation_code: bool
    join_code: bool
    admin_code: bool
    team_related: str | None


# =====================
# Dashboard Schemas
# =====================


class ZoneData(BaseModel):
    """Per-zone statistics for all metrics"""

    goals_for: int = 0
    goals_against: int = 0
    chances_for: int = 0
    chances_against: int = 0


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
    ice_zones: Dict[str, ZoneData]
    net_zones: Dict[str, ZoneData]
    player_stats: List[GamePlayerStats]


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
    ice_zones: Dict[str, ZoneData]
    net_zones: Dict[str, ZoneData]
    player_stats: List[GamePlayerStats]
    situations: Optional[Dict[str, "SituationKPI"]] = None


class DashboardResponse(BaseModel):
    team_name: str
    games: List[GameKPI]


# =====================
# Player Page Schemas
# =====================

class MarkerData(BaseModel):
    x: int
    y: int
    result: str

class PlayerTagData(BaseModel):
    id: int
    game_id: int
    date: str
    opponent: str
    home: bool
    strengths: str
    ice_x: int
    ice_y: int
    ice_zone: str
    net_x: int
    net_y: int
    net_zone: str
    net_height: str
    net_width: str
    shot_result: str
    shot_type: str
    is_shooter: bool
    is_participating: bool
    is_on_ice: bool

class PlayerGameMetadata(BaseModel):
    game_id: int
    date: str
    opponent: str
    home: bool

class ShotTypeStats(BaseModel):
    shot_type: str
    goals: int = 0
    chances: int = 0
    efficiency: float = 0.0

class GameTrendPoint(BaseModel):
    game_id: int
    opponent: str
    date: str
    goals: int
    chances: int
    rolling_goals: float
    rolling_chances: float
    team_rolling_goals: float
    team_rolling_chances: float

class SpiderChartKPI(BaseModel):
    label: str
    player_value: float
    team_avg: float

class SpiderChartData(BaseModel):
    kpis: List[SpiderChartKPI]

class SynergyDataPoint(BaseModel):
    teammate_id: int
    teammate_name: str
    jersey_number: int
    net_mp_per_game: float

class SynergyData(BaseModel):
    points: List[SynergyDataPoint]

class PlayerStatsResponse(BaseModel):
    player_id: int
    first_name: str
    last_name: str
    jersey_number: int
    position: str
    team_name: str
    summary: "SeasonSummaryKPIs"
    ice_zones: Dict[str, ZoneData]
    net_zones: Dict[str, ZoneData]
    ice_markers: List[MarkerData]
    net_markers: List[MarkerData]
    all_tags: List[PlayerTagData]
    all_games: List[PlayerGameMetadata]
    shot_type_stats: List[ShotTypeStats]
    trend_data: List[GameTrendPoint]
    team_avg_goals: float
    team_avg_chances: float
    spider_data: SpiderChartData
    synergy_data: SynergyData
    # Future components will add more fields here

class SeasonSummaryKPIs(BaseModel):
    games_played: int = 0
    goals: int = 0
    chances: int = 0
    efficiency: float = 0.0
    chances_per_game: float = 0.0
    participation_m_plus: int = 0
    participation_m_minus: int = 0
    participation_m_diff: int = 0
    participation_mp_plus: int = 0
    participation_mp_minus: int = 0
    participation_mp_diff: int = 0
    on_ice_m_plus: int = 0
    on_ice_m_minus: int = 0
    on_ice_m_diff: int = 0
    on_ice_mp_plus: int = 0
    on_ice_mp_minus: int = 0
    on_ice_mp_diff: int = 0
