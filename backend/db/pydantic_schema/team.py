from pydantic import BaseModel
from db.pydantic_schema.player import PlayerResponse

class TeamCreate(BaseModel):
    model_config = {"extra": "forbid"}
    name: str

class TeamCreateResponse(BaseModel):
    team_name: str
    code_for_team: str

class TeamResponse(BaseModel):
    team_name: str | None
    join_code: str | None
    players: list[PlayerResponse] | None
