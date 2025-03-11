from contextlib import asynccontextmanager
from datetime import datetime
from hashlib import md5
from json import dumps as json_dumps, loads as json_loads, JSONEncoder
from logging import getLogger
from os import getenv

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

logger = getLogger("cache")

REDIS_HOST = getenv("REDIS_HOST", "localhost")
REDIS_URL = getenv("REDIS_URL", "redis://localhost:6379")


class DateTimeEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(o)


@asynccontextmanager
async def lifespan(app):
    """Context manager to initialize and close Redis connection"""
    redis = aioredis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield
    await redis.close()


def generate_cache_key(date: str, origin: str, destination: str) -> str:
    """Generate a unique cache key"""
    raw_key = f"{date}-{origin}-{destination}"
    cache_key = md5(raw_key.encode()).hexdigest()
    return cache_key


async def get_cached_response(redis_client, cache_key):
    """Retrieve cached response if available"""
    if redis_client is None:
        return None
    cached_response = await redis_client.get(cache_key)
    if cached_response is None:
        return None
    return json_loads(cached_response)


async def set_cache_response(redis, cache_key, values, expiration=60):
    """Store response in Redis cache"""
    serialized_value = json_dumps(values, cls=DateTimeEncoder)

    await redis.setex(cache_key, expiration, serialized_value)
