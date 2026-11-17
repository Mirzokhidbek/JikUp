from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, agent, analytics, auth, health, jobs, resumes, search, skills
from app.core.auth import current_user
from app.core.config import get_settings
from app.core.db import engine
from app.core.logging import setup_logging
from app.core.rate_limit import DEFAULT, rate_limit
from app.core.redis import redis
from app.core.security_headers import add_security_headers

settings = get_settings()
setup_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.arq = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    yield
    await app.state.arq.aclose()
    await engine.dispose()
    await redis.aclose()


app = FastAPI(
    title="JikUp API",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_dev else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.is_dev else None,
    dependencies=[Depends(rate_limit(DEFAULT))],
)

app.middleware("http")(add_security_headers)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(admin.router)

# Everything in the portal needs a signed-in user.
signed_in = [Depends(current_user)]
for portal in (jobs, search, resumes, agent, skills, analytics):
    app.include_router(portal.router, dependencies=signed_in)
