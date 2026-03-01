import os
from redis import Redis


def get_redis():
    client = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)
    try:
        yield client
    finally:
        client.close()
