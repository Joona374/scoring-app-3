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
    team_name: str
    join_code: str
    players: List[PlayerResponse]

class PositionInRoster(BaseModel):
    line: int
    position: str
    player: Optional[PlayerResponse]

class GameCreate(BaseModel):
    opponent: str
    game_date: date
    home_game: bool
    players_in_roster: List[PositionInRoster]

class GameInRosterResponse(BaseModel):
    line: int
    position: str
    player: PlayerResponse
    
class TeamStatsTagResponse(BaseModel):
    id: Optional[int]
    succes: bool
    tag: dict