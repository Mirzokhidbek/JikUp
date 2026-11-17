from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, end_session, start_session
from app.core.db import get_session
from app.core.rate_limit import AUTH, rate_limit
from app.core.redis import get_redis
from app.schemas.auth import Credentials, UserOut
from app.services.users import EmailTaken, authenticate, create_user

router = APIRouter(prefix="/auth", tags=["auth"])

Session = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[Redis, Depends(get_redis)]
limited = [Depends(rate_limit(AUTH))]


@router.post("/register", status_code=status.HTTP_201_CREATED, dependencies=limited)
async def register(
    body: Credentials, session: Session, redis: RedisDep, response: Response
) -> UserOut:
    try:
        user = await create_user(session, body.email, body.password)
    except EmailTaken:
        raise HTTPException(status.HTTP_409_CONFLICT, "This email is already registered") from None
    await start_session(redis, response, user)
    return UserOut(id=user.id, email=user.email)


@router.post("/login", dependencies=limited)
async def login(
    body: Credentials, session: Session, redis: RedisDep, response: Response
) -> UserOut:
    user = await authenticate(session, body.email, body.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong email or password")
    await start_session(redis, response, user)
    return UserOut(id=user.id, email=user.email)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, redis: RedisDep) -> Response:
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    await end_session(redis, request, response)
    return response


@router.get("/me")
async def me(user: User) -> UserOut:
    return UserOut(id=user.id, email=user.email)
