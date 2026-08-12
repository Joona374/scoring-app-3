from pydantic import BaseModel
from db.models import Positions


class PlayerCreate(BaseModel):
    model_config = {"extra": "forbid"}
    first_name: str
    last_name: str
    jersey_number: int
    position: Positions


class PlayerUpdate(BaseModel):
    first_name: str | None
    last_name: str | None
    jersey_number: int | None
    position: Positions | None


class PlayerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    jersey_number: int
    position: str
