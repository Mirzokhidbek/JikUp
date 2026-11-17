from collections.abc import AsyncIterator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import COOKIE_NAME
from app.core.db import get_session
from app.core.passwords import hash_password, verify_password
from app.core.redis import get_redis
from app.main import app
from app.models import User
from app.schemas.auth import Credentials

pytestmark = pytest.mark.real_auth

PASSWORD = "correct horse battery"  # noqa: S105 (test value)


class FakeRedis:
    def __init__(self, fail: bool = False) -> None:
        self.data: dict[str, Any] = {}
        self.ttl: dict[str, int] = {}
        self.fail = fail

    async def set(self, key: str, value: str, ex: int) -> None:
        self.data[key], self.ttl[key] = value, ex

    async def get(self, key: str) -> Any:
        if self.fail:
            raise ConnectionError
        return self.data.get(key)

    async def expire(self, key: str, seconds: int) -> bool:
        self.ttl[key] = seconds
        return True

    async def delete(self, key: str) -> int:
        return 1 if self.data.pop(key, None) is not None else 0

    async def incr(self, key: str) -> int:
        return 1


def test_password_hashing() -> None:
    hashed = hash_password(PASSWORD)
    assert hashed.startswith("$argon2id$") and PASSWORD not in hashed
    assert verify_password(hashed, PASSWORD)
    assert not verify_password(hashed, "wrong password")
    assert not verify_password(None, PASSWORD)
    assert not verify_password("garbage", PASSWORD)


@pytest.mark.parametrize(
    ("email", "password"),
    [("no-at-sign", PASSWORD), ("a@b", PASSWORD), ("a@b.co", "short"), ("a@b.co", "x" * 129)],
)
def test_credentials_are_validated(email: str, password: str) -> None:
    with pytest.raises(ValidationError):
        Credentials(email=email, password=password)


def test_email_is_normalized() -> None:
    assert Credentials(email="  Me@Example.COM ", password=PASSWORD).email == "me@example.com"


@pytest.fixture
async def ctx(db_session: AsyncSession) -> AsyncIterator[tuple[AsyncClient, FakeRedis]]:
    redis = FakeRedis()

    async def session_override() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = session_override
    app.dependency_overrides[get_redis] = lambda: redis
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c, redis
    app.dependency_overrides.clear()


async def test_register_login_logout(
    ctx: tuple[AsyncClient, FakeRedis], db_session: AsyncSession
) -> None:
    c, redis = ctx
    assert (await c.get("/jobs")).status_code == 401
    assert (await c.get("/auth/me")).status_code == 401

    res = await c.post("/auth/register", json={"email": "New@Example.com", "password": PASSWORD})
    assert res.status_code == 201 and res.json()["email"] == "new@example.com"
    cookie = res.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie
    token = c.cookies[COOKIE_NAME]
    assert token not in str(redis.data)  # only a hash of the token is stored
    stored = (await db_session.execute(select(User.password_hash))).scalars().all()
    assert all(PASSWORD not in h for h in stored)

    assert (await c.get("/auth/me")).json()["email"] == "new@example.com"
    assert (await c.get("/jobs")).status_code == 200

    assert (await c.post("/auth/logout")).status_code == 204
    c.cookies.set(COOKIE_NAME, token)  # a copied cookie must not work after logout
    assert (await c.get("/auth/me")).status_code == 401

    c.cookies.clear()
    bad = await c.post("/auth/login", json={"email": "new@example.com", "password": "wrong pass"})
    assert bad.status_code == 401 and bad.json()["detail"] == "Wrong email or password"
    unknown = await c.post(
        "/auth/login", json={"email": "nobody@example.com", "password": PASSWORD}
    )
    assert unknown.status_code == 401 and unknown.json()["detail"] == bad.json()["detail"]

    ok = await c.post("/auth/login", json={"email": "NEW@example.com", "password": PASSWORD})
    assert ok.status_code == 200 and c.cookies[COOKIE_NAME] != token


async def test_duplicate_email_is_rejected(ctx: tuple[AsyncClient, FakeRedis]) -> None:
    c, _ = ctx
    body = {"email": "dup@example.com", "password": PASSWORD}
    assert (await c.post("/auth/register", json=body)).status_code == 201
    assert (await c.post("/auth/register", json=body)).status_code == 409


async def test_forged_cookie_and_store_outage(ctx: tuple[AsyncClient, FakeRedis]) -> None:
    c, redis = ctx
    c.cookies.set(COOKIE_NAME, "forged")
    assert (await c.get("/auth/me")).status_code == 401
    redis.fail = True
    assert (await c.get("/auth/me")).status_code == 503


@pytest.mark.parametrize(
    "path", ["/jobs", "/skills", "/analytics/overview", "/resumes/" + "0" * 32]
)
async def test_portal_requires_login(path: str) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        assert (await c.get(path)).status_code == 401
