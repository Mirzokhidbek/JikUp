from collections.abc import AsyncIterator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.db import get_session
from app.core.redis import get_redis
from app.main import app


class FakeSession:
    async def execute(self, _: Any) -> None:
        return None


class FakeRedis:
    def __init__(self, fail: bool) -> None:
        self.fail = fail

    async def ping(self) -> bool:
        if self.fail:
            raise ConnectionError
        return True


async def fake_session() -> AsyncIterator[FakeSession]:
    yield FakeSession()


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    app.dependency_overrides[get_session] = fake_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def test_health_ok(client: AsyncClient) -> None:
    app.dependency_overrides[get_redis] = lambda: FakeRedis(fail=False)
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "db": "ok", "redis": "ok"}


async def test_health_reports_failed_dependency(client: AsyncClient) -> None:
    app.dependency_overrides[get_redis] = lambda: FakeRedis(fail=True)
    res = await client.get("/health")
    assert res.status_code == 503
    assert res.json() == {"status": "degraded", "db": "ok", "redis": "error"}
