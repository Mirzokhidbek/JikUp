import hashlib
import json
import logging
import secrets
import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, Response, status
from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.redis import get_redis

log = logging.getLogger(__name__)

COOKIE_NAME = "jikup_session"


@dataclass(frozen=True)
class CurrentUser:
    id: uuid.UUID
    email: str


def _key(token: str) -> str:
    # Only a hash of the token is stored, so a Redis dump cannot be replayed as cookies.
    return f"sess:{hashlib.sha256(token.encode()).hexdigest()}"


def _ttl() -> int:
    return get_settings().session_days * 86400


async def start_session(redis: Redis, response: Response, user: CurrentUser) -> None:
    token = secrets.token_urlsafe(32)
    payload = json.dumps({"id": str(user.id), "email": user.email})
    await redis.set(_key(token), payload, ex=_ttl())
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=_ttl(),
        httponly=True,
        secure=get_settings().cookie_secure,
        samesite="lax",
        path="/",
    )


async def end_session(redis: Redis, request: Request, response: Response) -> None:
    token = request.cookies.get(COOKIE_NAME)
    if token:
        await redis.delete(_key(token))
    response.delete_cookie(COOKIE_NAME, path="/")


async def current_user(
    request: Request, redis: Annotated[Redis, Depends(get_redis)]
) -> CurrentUser:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed in")
    key = _key(token)
    try:
        raw = await redis.get(key)
        if raw is not None:
            await redis.expire(key, _ttl())
    except Exception as exc:
        log.warning("session store unavailable (%s)", type(exc).__name__)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Try again later") from None
    if raw is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed in")
    data = json.loads(raw)
    return CurrentUser(id=uuid.UUID(data["id"]), email=data["email"])


User = Annotated[CurrentUser, Depends(current_user)]
