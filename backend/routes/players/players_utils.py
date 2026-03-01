import logging
from redis import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


def get_cache_key_for_team_players(team_id: int) -> str:
    return f"team:{team_id}:players"

def invalidate_team_cache(team_id: int, redis_client: Redis):
    """
    Deletes the cached player list for a team.
    Fails gracefully if Redis is down.
    """
    cache_key = get_cache_key_for_team_players(team_id)

    try:
        redis_client.delete(cache_key)
        logger.info(f"🗑️ Cache busted for team {team_id}")
    except RedisError as e:
        logger.warning(f"⚠️ Failed to invalidate cache for team {team_id}: {e}")
