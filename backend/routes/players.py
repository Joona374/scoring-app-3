from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.pydantic_schemas import PlayerCreate
from db.db_manager import get_db_session

router = APIRouter(
    prefix="/players",
    tags=["players"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
def create_a_player(player_data: PlayerCreate, db_session: Session = Depends(get_db_session)):
    player_first_name = player_data.first_name
    player_last_name = player_data.last_name
    player_position = player_data.position

    print(f"Player: {player_first_name} {player_last_name} is {player_position}")