from redis.asyncio import Redis

from app.core.config import get_settings

redis: Redis = Redis.from_url(get_settings().redis_url)


def get_redis() -> Redis:
    return redis
