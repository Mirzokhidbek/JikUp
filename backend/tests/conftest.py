import os
import uuid
from collections.abc import AsyncIterator, Iterator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

TEST_USER_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
TEST_USER_EMAIL = "tester@example.com"


@pytest.fixture(autouse=True)
def signed_in(request: pytest.FixtureRequest) -> Iterator[None]:
    """API tests run as TEST_USER unless marked real_auth."""
    if request.node.get_closest_marker("real_auth"):
        yield
        return
    from app.core.auth import CurrentUser, current_user
    from app.main import app

    app.dependency_overrides[current_user] = lambda: CurrentUser(TEST_USER_ID, TEST_USER_EMAIL)
    yield
    app.dependency_overrides.pop(current_user, None)


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL is not set")
    from app.models import Base

    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text("INSERT INTO users (id, email, password_hash) VALUES (:id, :email, 'x')"),
            {"id": TEST_USER_ID, "email": TEST_USER_EMAIL},
        )
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        yield session
    await engine.dispose()
