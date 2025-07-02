from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.pydantic_schemas import PlayerCreate
from db.db_manager import get_db_session
from db.models import Player, User
from utils import get_current_user_id

router = APIRouter(
    prefix="/games",
    tags=["games"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
def create_game(data, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    print(data)