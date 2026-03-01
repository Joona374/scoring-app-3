import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from redis import Redis

from db.pydantic_schemas import PlayerResponse, PlayerUpdate
from routes.players.players_utils import invalidate_team_cache
from db.db_manager import get_db_session
from db.models import Player, User, Team
from db.redis_client import get_redis
from utils import get_current_user_and_team

router = APIRouter()
logger = logging.getLogger(__name__)

@router.patch("/update/{player_id}")
def update_player(player_id: int, player_data: PlayerUpdate, db_session: Session = Depends(get_db_session), user_and_team: tuple["User", "Team"] = Depends(get_current_user_and_team), redis_client: Redis = Depends(get_redis) # fmt: skip
):
    user, team = user_and_team
    player = db_session.query(Player).filter(Player.id == player_id).first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    if user.team != player.team:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No permission to edit this player")

    update_data = player_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(player, key, value)

    db_session.commit()
    db_session.refresh(player)

    invalidate_team_cache(team.id, redis_client)

    return PlayerResponse(id=player.id, first_name=player.first_name, last_name=player.last_name, jersey_number=player.jersey_number, position=player.position.name)
