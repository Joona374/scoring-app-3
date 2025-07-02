from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.pydantic_schemas import PlayerCreate, PlayerResponse
from db.db_manager import get_db_session
from db.models import Player, User
from utils import get_current_user_id

router = APIRouter(
    prefix="/players",
    tags=["players"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
def create_a_player(player_data: PlayerCreate, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    player_first_name = player_data.first_name
    player_last_name = player_data.last_name
    player_position = player_data.position

    print(f"Player: {player_first_name} {player_last_name} is {player_position}")
    user = db_session.query(User).filter(User.id == current_user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found in db")

    new_player = Player(
        first_name=player_first_name,
        last_name=player_last_name,
        position=player_position,
        team=user.team
    )

    db_session.add(new_player)
    db_session.commit()
    db_session.refresh(new_player)

    return {"message": "Player created successfully", "player_name": f"{player_first_name} {player_last_name}", "creator_id": current_user_id}

@router.get("/for-team")
def get_player_for_team(db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    user = db_session.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found in db")

    team = user.team
    teams_players = team.players

    response_players_list = []
    for player in teams_players:
        player_response = PlayerResponse(
            first_name=player.first_name,
            last_name=player.last_name,
            position=player.position.name
        )
        response_players_list.append(player_response)

    return response_players_list