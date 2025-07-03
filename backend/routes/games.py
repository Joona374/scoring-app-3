from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.pydantic_schemas import GameCreate
from db.db_manager import get_db_session
from db.models import Player, User, Game, GameInRoster
from utils import get_current_user_id

router = APIRouter(
    prefix="/games",
    tags=["games"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
def create_game(data: GameCreate, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    user = db_session.query(User).filter(User.id == current_user_id).first()

    new_game = Game(
        date=data.game_date,
        opponent=data.opponent,
        home=data.home_game,
        team=user.team
    )
    
    for position in data.players_in_roster:
        if position.player:
            new_game_in_roster = GameInRoster(
                line=position.line,
                position=position.position,
                player_id=position.player.id
            )
            new_game.in_rosters.append(new_game_in_roster)

    db_session.add(new_game)
    db_session.commit()