import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.redis import get_redis

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Limit:
    name: str
    count: int
    seconds: int


DEFAULT = Limit("default", 120, 60)
SEARCH = Limit("search", 20, 60)
RESUME_UPLOAD = Limit("resume", 10, 3600)
AGENT_RUN = Limit("agent", 5, 3600)
AUTH = Limit("auth", 10, 60)


def client_ip(request: Request) -> str:
    # Forwarded headers are client-controlled; trust them only behind a configured proxy.
    return request.client.host if request.client else "unknown"


def rate_limit(limit: Limit) -> Callable[..., Awaitable[None]]:
    async def check(request: Request, redis: Annotated[Redis, Depends(get_redis)]) -> None:
        if not get_settings().rate_limit_enabled:
            return
        now = int(time.time())
        key = f"rl:{limit.name}:{client_ip(request)}:{now // limit.seconds}"
        try:
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, limit.seconds)
        except Exception as exc:
            log.warning("rate limiter unavailable, allowing request (%s)", type(exc).__name__)
            return
        if count > limit.count:
            retry_after = limit.seconds - now % limit.seconds
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                f"Too many requests. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

    return check
