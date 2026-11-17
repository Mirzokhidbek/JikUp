import asyncio
import logging
from collections.abc import Awaitable
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Response, status
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.redis import get_redis

router = APIRouter(tags=["health"])
log = logging.getLogger(__name__)

CHECK_TIMEOUT_S = 2


async def _check(name: str, probe: Awaitable[Any]) -> str:
    try:
        async with asyncio.timeout(CHECK_TIMEOUT_S):
            await probe
        return "ok"
    except Exception as exc:
        log.warning("health check failed: %s (%s)", name, type(exc).__name__)
        return "error"


@router.get("/health")
async def health(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> dict[str, str]:
    checks = {
        "db": await _check("db", session.execute(text("SELECT 1"))),
        "redis": await _check("redis", redis.ping()),
    }
    healthy = all(result == "ok" for result in checks.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ok" if healthy else "degraded", **checks}
