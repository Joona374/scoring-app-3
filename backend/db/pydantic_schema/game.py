from db.pydantic_schema.player import PlayerResponse
from pydantic import BaseModel
from datetime import date


class PositionInRoster(BaseModel):
    line: int
    position: str
    player: PlayerResponse | None


class GameCreate(BaseModel):
    opponent: str
    game_date: date
    home_game: bool
    players_in_roster: list[PositionInRoster]
    powerplays: int | None = 0
    penalty_kills: int | None = 0


class GameInRosterResponse(BaseModel):
    line: int
    position: str
    player: PlayerResponse | None
