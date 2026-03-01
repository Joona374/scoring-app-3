import logging
from redis import Redis
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.pydantic_schemas import PlayerCreate
from db.db_manager import get_db_session
from db.models import Player, Team, User
from db.redis_client import get_redis
from utils import get_current_user_and_team
from routes.players.players_utils import invalidate_team_cache

router = APIRouter()
logger = logging.getLogger(__name__)

def create_new_player_entry(player_data: PlayerCreate, team: Team) -> Player:
    player_first_name = player_data.first_name
    player_last_name = player_data.last_name
    player_jersey_number = player_data.jersey_number
    player_position = player_data.position

    return Player(first_name=player_first_name, last_name=player_last_name, jersey_number=player_jersey_number, position=player_position, team=team)

@router.post("/create")
def create_a_player(
    player_data: PlayerCreate, 
    db_session: Session = Depends(get_db_session), 
    user_and_team: tuple["User", "Team"] = Depends(get_current_user_and_team), 
    redis_client: Redis = Depends(get_redis) # fmt: skip
):
    user, team = user_and_team
    new_player = create_new_player_entry(player_data, team)

    db_session.add(new_player)
    db_session.commit()
    db_session.refresh(new_player)

    invalidate_team_cache(team.id, redis_client)

    return {"message": "Player created successfully", "player_name": f"{new_player.first_name} {new_player.last_name}", "creator_id": user.id, "player_id": new_player.id}
