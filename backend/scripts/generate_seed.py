"""Generate synthetic Korean IT job postings for demo and tests.

Usage (from backend/): uv run python -m scripts.generate_seed [--batches 20]
All companies are fictional. Appends to data/seed_jobs.jsonl after each batch, so a rerun
resumes where the last run stopped.
"""

import argparse
import asyncio
import json
import logging
from datetime import UTC, datetime, timedelta

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.collectors.seed import SEED_PATH
from app.core.config import get_settings
from app.core.logging import setup_logging

BATCH_SIZE = 10
CONCURRENCY = 4
ROLES = [
    "백엔드 개발자 (Java/Spring 또는 Python/Go)",
    "프론트엔드 개발자 (React/Vue/TypeScript)",
    "AI/ML 엔지니어 (PyTorch, 모델 학습/서빙)",
    "LLM 애플리케이션 개발자 (RAG, LangChain, 프롬프트)",
    "데이터 엔지니어 (Spark, Airflow, Kafka)",
    "데이터 분석가 (SQL, Python, 통계, BI)",
    "DevOps/SRE (AWS, Kubernetes, Terraform)",
    "모바일 개발자 (iOS Swift 또는 Android Kotlin, Flutter)",
    "풀스택 개발자 (Node.js, React, 스타트업)",
    "MLOps 엔지니어 (MLflow, Kubeflow, 모델 배포)",
]

log = logging.getLogger("generate_seed")


class SeedPosting(BaseModel):
    title: str
    company: str = Field(description="Fictional Korean company name, never a real company")
    location: str = Field(description="예: '서울 강남구', '경기 성남시', '부산 해운대구'")
    experience: str = Field(description="예: '신입', '경력 3년 이상', '1~3년', '경력무관'")
    employment_type: str = Field(description="정규직, 계약직, 인턴 중 하나")
    salary: str = Field(description="예: '회사내규에 따름', '4,000~6,000만원'")
    description: str = Field(description="회사 소개 후 주요업무/자격요건/우대사항/복지 섹션")
    posted_days_ago: int = Field(ge=0, le=60)
    deadline_in_days: int = Field(ge=1, le=60)


def build_prompt(role: str) -> str:
    return f"""한국 IT 채용 공고 {BATCH_SIZE}개를 JSON으로 작성하세요. 직무: {role}

규칙:
- 회사명은 모두 가상의 이름이어야 합니다. 실제 존재하는 회사명은 절대 사용하지 마세요.
- 실제 사람인/원티드 공고처럼 자연스러운 한국어로 작성하세요.
- 공고마다 지역(서울 외 경기, 부산, 대전, 판교 등 포함), 경력 조건, 고용형태,
  회사 규모를 다양하게 하세요.
- description은 짧은 회사 소개 후 각 섹션 제목을 별도 줄에 쓰세요.
  섹션 제목 표기를 다양하게: [주요업무], ■ 담당업무, 자격요건:, 필수요건, 우대사항, 혜택 및 복지 등.
- 각 섹션은 3~6개의 bullet로 구체적인 기술 스택을 포함하세요.
  한글/영문 표기를 섞어 쓰세요 (예: 파이썬, Python).
"""


async def generate_batch(client: genai.Client, model: str, role: str) -> list[SeedPosting]:
    response = await client.aio.models.generate_content(
        model=model,
        contents=build_prompt(role),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[SeedPosting],
            temperature=1.0,
        ),
    )
    parsed = response.parsed
    if not isinstance(parsed, list):
        raise RuntimeError(f"Model returned no parsable postings for role: {role}")
    return [p for p in parsed if isinstance(p, SeedPosting)]


def to_record(index: int, posting: SeedPosting, now: datetime) -> dict[str, str]:
    return {
        "id": f"seed-{index:04d}",
        "title": posting.title,
        "company": posting.company,
        "location": posting.location,
        "experience": posting.experience,
        "employment_type": posting.employment_type,
        "salary": posting.salary,
        "description": posting.description.replace("\\n", "\n"),
        "posted_at": (now - timedelta(days=posting.posted_days_ago)).isoformat(),
        "deadline_at": (now + timedelta(days=posting.deadline_in_days)).isoformat(),
    }


def existing_count() -> int:
    if not SEED_PATH.exists():
        return 0
    with SEED_PATH.open(encoding="utf-8") as lines:
        return sum(1 for line in lines if line.strip())


async def main(batches: int) -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    api_key = settings.gemini_api_key.get_secret_value()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is not set")

    existing = existing_count()
    first_batch = existing // BATCH_SIZE
    if first_batch >= batches:
        log.info("already have %d postings, nothing to do", existing)
        return

    client = genai.Client(api_key=api_key)
    now = datetime.now(UTC).replace(microsecond=0)
    limit = asyncio.Semaphore(CONCURRENCY)
    write_lock = asyncio.Lock()
    next_index = existing + 1

    async def run(batch: int) -> None:
        nonlocal next_index
        role = ROLES[batch % len(ROLES)]
        async with limit:
            postings = await generate_batch(client, settings.gemini_chat_model, role)
        async with write_lock:
            records = [to_record(next_index + i, p, now) for i, p in enumerate(postings)]
            next_index += len(records)
            with SEED_PATH.open("a", encoding="utf-8") as out:
                out.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
        log.info("batch %d/%d saved: %d postings (%s)", batch + 1, batches, len(records), role)

    results = await asyncio.gather(
        *(run(batch) for batch in range(first_batch, batches)), return_exceptions=True
    )
    for error in (r for r in results if isinstance(r, BaseException)):
        log.warning("batch failed: %s", type(error).__name__)
    log.info("seed file now has %d postings", existing_count())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batches", type=int, default=20)
    asyncio.run(main(parser.parse_args().batches))
