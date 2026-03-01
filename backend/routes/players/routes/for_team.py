import json
import logging
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.encoders import jsonable_encoder
from redis import Redis
from redis.exceptions import RedisError
from pydantic import TypeAdapter

from db.pydantic_schemas import PlayerResponse
from db.redis_client import get_redis
from db.models import Team, User
from utils import get_current_user_and_team
from routes.players.players_utils import get_cache_key_for_team_players

router = APIRouter()
logger = logging.getLogger(__name__)

def build_response_players_list(team: "Team") -> list[PlayerResponse]:
    teams_players = team.players
    response_players_list = []
    for player in teams_players:
        if not player.is_active:
            continue
        player_response = PlayerResponse(id=player.id, first_name=player.first_name, last_name=player.last_name, jersey_number=player.jersey_number, position=player.position.name)
        response_players_list.append(player_response)
    return response_players_list

def get_players_from_cache(redis_client: Redis, cache_key: str):
    cached_data = cast(str | None, redis_client.get(cache_key))
    if cached_data:
        logger.info(f"⚡ Cache Hit for Team {cache_key}")
        return cached_data

def get_and_validate_players_from_db(team: "Team") -> list[PlayerResponse]:
    response_players_list = build_response_players_list(team)

    adapter = TypeAdapter(list[PlayerResponse])
    validated_players = adapter.validate_python(response_players_list)
    return validated_players

def add_players_to_cache(validated_players: list[PlayerResponse], redis_client: Redis, cache_key: str) -> None:
    json_compatible_list = jsonable_encoder(validated_players)
    redis_client.set(cache_key, json.dumps(json_compatible_list), ex=3600)


@router.get("/for-team")
def get_player_for_team(user_and_team: tuple["User", "Team"] = Depends(get_current_user_and_team), redis_client: Redis = Depends(get_redis)):
    _, team = user_and_team
    cache_key = get_cache_key_for_team_players(team.id)

    # 1. If the data is in cache, return it immediately
    try:
        cached_data = get_players_from_cache(redis_client, cache_key)
        if cached_data:
            return Response(content=cached_data, media_type="application/json")
    except RedisError as e:
        logger.warning(f"⚠️ Redis error: {e}. Proceeding without cache.")
        pass

    # If not in cache, fetch from DB, validate, add to cache and return
    validated_players = get_and_validate_players_from_db(team)
    try:
        add_players_to_cache(validated_players, redis_client, cache_key)
    except RedisError as e:
        logger.warning(f"⚠️ Redis error while setting cache: {e}. Proceeding without caching.")
    
    return validated_players
    