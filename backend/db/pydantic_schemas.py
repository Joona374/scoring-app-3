from pydantic import BaseModel, EmailStr, field_validator
from db.models import Positions
from typing import Optional, List, Dict
from datetime import date

class UserCreate(BaseModel):
    model_config = {"extra": "forbid"}

    username: str
    email: EmailStr
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
    position: str  # This would be "FORWARD", "DEFENDER", etc.

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
    team_related: str | None # Just the name of the team


# =====================
# Dashboard Schemas
# =====================


class ZoneData(BaseModel):
    """Per-zone statistics for all metrics"""

    goals_for: int = 0
    goals_against: int = 0
    chances_for: int = 0  # includes goals
    chances_against: int = 0  # includes goals


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


class GameKPI(BaseModel):
    game_id: int
    date: str
    opponent: str
    home: bool
    goals_for: int
    goals_against: int
    chances_for: int
    chances_against: int
    efficiency_for: float  # goals_for / chances_for * 100
    efficiency_against: float  # goals_against / chances_against * 100
    ice_zones: Dict[str, ZoneData]  # Zone breakdown for this game
    net_zones: Dict[str, ZoneData]  # Net zone breakdown for this game
    player_stats: List[GamePlayerStats]  # Per-player stats for this game


class DashboardResponse(BaseModel):
    team_name: str
    games: List[GameKPI]  # All games with per-game zone and player stats
