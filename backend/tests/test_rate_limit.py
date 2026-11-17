from typing import Any

import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.core.rate_limit import Limit, rate_limit
from app.core.redis import get_redis
from app.core.security_headers import add_security_headers
from app.main import app as main_app


class FakeRedis:
    def __init__(self, fail: bool = False) -> None:
        self.counts: dict[str, int] = {}
        self.fail = fail

    async def incr(self, key: str) -> int:
        if self.fail:
            raise ConnectionError
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def expire(self, key: str, seconds: int) -> bool:
        return True


def make_app(redis: FakeRedis) -> FastAPI:
    app = FastAPI()

    @app.get("/limited", dependencies=[Depends(rate_limit(Limit("test", 2, 60)))])
    async def limited() -> dict[str, bool]:
        return {"ok": True}

    app.dependency_overrides[get_redis] = lambda: redis
    return app


@pytest.fixture
def enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "rate_limit_enabled", True)


async def client_for(app: FastAPI, ip: str) -> AsyncClient:
    transport = ASGITransport(app=app, client=(ip, 1234))
    return AsyncClient(transport=transport, base_url="http://test")


async def statuses(app: FastAPI, ip: str, n: int) -> list[int]:
    async with await client_for(app, ip) as c:
        return [(await c.get("/limited")).status_code for _ in range(n)]


async def test_limit_returns_429_with_retry_after(enabled: None) -> None:
    app = make_app(FakeRedis())
    async with await client_for(app, "1.1.1.1") as c:
        codes = [(await c.get("/limited")).status_code for _ in range(3)]
        last = await c.get("/limited")
    assert codes == [200, 200, 429]
    assert 0 < int(last.headers["retry-after"]) <= 60
    assert "Too many requests" in last.json()["detail"]


async def test_limit_is_per_client(enabled: None) -> None:
    app = make_app(FakeRedis())
    assert await statuses(app, "1.1.1.1", 3) == [200, 200, 429]
    assert await statuses(app, "2.2.2.2", 1) == [200]


async def test_forwarded_header_does_not_bypass(enabled: None) -> None:
    app = make_app(FakeRedis())
    async with await client_for(app, "1.1.1.1") as c:
        codes = [
            (await c.get("/limited", headers={"X-Forwarded-For": f"9.9.9.{i}"})).status_code
            for i in range(3)
        ]
    assert codes == [200, 200, 429]


async def test_redis_failure_allows_requests(enabled: None) -> None:
    assert await statuses(make_app(FakeRedis(fail=True)), "1.1.1.1", 3) == [200, 200, 200]


async def test_disabled_by_setting() -> None:
    assert await statuses(make_app(FakeRedis()), "1.1.1.1", 3) == [200, 200, 200]


async def test_security_headers_on_api_responses() -> None:
    app = FastAPI()
    app.middleware("http")(add_security_headers)

    @app.get("/x")
    async def x() -> dict[str, Any]:
        return {}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        headers = (await c.get("/x")).headers
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert headers["content-security-policy"].startswith("default-src 'none'")


@pytest.mark.parametrize(("path", "allowed"), [("/agent/run", 5), ("/resumes", 10)])
async def test_expensive_endpoints_are_limited(enabled: None, path: str, allowed: int) -> None:
    shared = FakeRedis()
    main_app.dependency_overrides[get_redis] = lambda: shared
    try:
        async with await client_for(main_app, "3.3.3.3") as c:
            codes = [(await c.post(path, json={})).status_code for _ in range(allowed + 1)]
    finally:
        main_app.dependency_overrides.clear()
    assert 429 not in codes[:allowed]
    assert codes[allowed] == 429
