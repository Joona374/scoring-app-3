import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from redis import Redis

from routes.players.players_utils import invalidate_team_cache
from db.db_manager import get_db_session
from db.models import Player, User, Team
from db.redis_client import get_redis
from utils import get_current_user_and_team

router = APIRouter()
logger = logging.getLogger(__name__)

@router.delete("/delete/{player_id}")
def delete_player(player_id: int, db_session: Session = Depends(get_db_session), user_and_team: tuple["User", "Team"] = Depends(get_current_user_and_team), redis_client: Redis = Depends(get_redis) # fmt: skip
):
    # This is a soft delete, just sets is_active to False
    user, _ = user_and_team
    player = db_session.query(Player).filter(Player.id == player_id).first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    if user.team != player.team:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No permission to delete this player")

    player.is_active = False
    db_session.commit()

    invalidate_team_cache(player.team.id, redis_client)

    return {"message": "Player deleted successfully", "success": True}