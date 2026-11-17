import uuid
from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, current_user
from app.core.db import get_session
from app.core.llm import get_llm_client
from app.main import app
from app.models import Resume
from app.nlp.skills import get_matcher
from app.resumes.parser import ParsedResume, Project, canonicalize
from app.resumes.pdf import MAX_BYTES, MAX_PAGES, ResumeFileError, extract_text
from app.services.resumes import purge_expired
from tests.pdf_factory import RESUME_LINES, make_pdf

PARSED = ParsedResume(
    name="Aziz Karimov",
    skills=["Python", "fastapi", "파이썬", "Clean Architecture"],
    years_experience=2,
    projects=[Project(title="Delivery API", stack=["Redis", "FastAPI"], impact="-40% latency")],
)


def test_extract_text_reads_pdf() -> None:
    text = extract_text(make_pdf(RESUME_LINES))
    assert "Aziz Karimov" in text and "TOPIK 4" in text


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (b"x" * (MAX_BYTES + 1), "larger than 5 MB"),
        (b"PK\x03\x04 not a pdf", "not a PDF"),
        (b"%PDF-1.7 broken", "could not be read"),
        (make_pdf(["short"]), "No text found"),
        (make_pdf(RESUME_LINES, pages=MAX_PAGES + 1), "more than"),
    ],
)
def test_extract_text_rejects_bad_files(data: bytes, message: str) -> None:
    with pytest.raises(ResumeFileError, match=message):
        extract_text(data)


def test_canonicalize_maps_skills_and_keeps_unknown() -> None:
    result = canonicalize(PARSED, get_matcher())
    assert result.skills == ["FastAPI", "Python", "Redis"]
    assert result.other_skills == ["Clean Architecture"]


def test_canonicalize_drops_impossible_years() -> None:
    assert (
        canonicalize(
            PARSED.model_copy(update={"years_experience": 99}), get_matcher()
        ).years_experience
        is None
    )


class FakeModels:
    def __init__(self, result: Any) -> None:
        self.result = result
        self.prompts: list[str] = []

    async def generate_content(self, *, model: str, contents: str, config: Any) -> Any:
        self.prompts.append(contents)
        return SimpleNamespace(parsed=self.result)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[tuple[AsyncClient, FakeModels]]:
    models = FakeModels(PARSED)

    async def session_override() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = session_override
    app.dependency_overrides[get_llm_client] = lambda: SimpleNamespace(
        aio=SimpleNamespace(models=models)
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c, models
    app.dependency_overrides.clear()


async def upload(c: AsyncClient, data: bytes, name: str = "../../aziz resume.pdf") -> Any:
    return await c.post("/resumes", files={"file": (name, data, "application/pdf")})


async def test_upload_read_delete(client: tuple[AsyncClient, FakeModels]) -> None:
    c, models = client
    res = await upload(c, make_pdf(RESUME_LINES))
    assert res.status_code == 201
    body = res.json()
    resume_id = body["id"]
    assert uuid.UUID(resume_id).version == 4
    assert body["filename"] == "aziz resume.pdf"
    assert body["parsed"]["skills"] == ["FastAPI", "Python", "Redis"]
    assert "Aziz Karimov" in models.prompts[0]

    assert (await c.get(f"/resumes/{resume_id}")).json()["parsed"]["name"] == "Aziz Karimov"
    assert (await c.delete(f"/resumes/{resume_id}")).status_code == 204
    assert (await c.get(f"/resumes/{resume_id}")).status_code == 404
    assert (await c.delete(f"/resumes/{resume_id}")).status_code == 404


async def test_other_user_cannot_see_or_delete(client: tuple[AsyncClient, FakeModels]) -> None:
    c, _ = client
    resume_id = (await upload(c, make_pdf(RESUME_LINES))).json()["id"]
    app.dependency_overrides[current_user] = lambda: CurrentUser(uuid.uuid4(), "other@example.com")
    assert (await c.get(f"/resumes/{resume_id}")).status_code == 404
    assert (await c.delete(f"/resumes/{resume_id}")).status_code == 404


async def test_upload_rejects_bad_file(client: tuple[AsyncClient, FakeModels]) -> None:
    c, models = client
    res = await upload(c, b"not a pdf at all")
    assert res.status_code == 422 and res.json()["detail"] == "File is not a PDF"
    assert models.prompts == []


async def test_upload_reports_parse_failure(client: tuple[AsyncClient, FakeModels]) -> None:
    c, models = client
    models.result = None
    assert (await upload(c, make_pdf(RESUME_LINES))).status_code == 502


async def test_invalid_id_is_rejected(client: tuple[AsyncClient, FakeModels]) -> None:
    c, _ = client
    assert (await c.get("/resumes/1")).status_code == 422


async def test_expired_resume_is_hidden_and_purged(
    client: tuple[AsyncClient, FakeModels], db_session: AsyncSession
) -> None:
    c, _ = client
    resume_id = (await upload(c, make_pdf(RESUME_LINES))).json()["id"]
    await db_session.execute(
        update(Resume)
        .where(Resume.id == uuid.UUID(resume_id))
        .values(expires_at=text("now() - interval '1 minute'"))
    )
    await db_session.commit()
    assert (await c.get(f"/resumes/{resume_id}")).status_code == 404
    assert await purge_expired(db_session) == 1
    assert await purge_expired(db_session) == 0
