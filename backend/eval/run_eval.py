"""Measure RAG quality on eval/rag_queries.yaml against the current database.

Usage (from backend/, DB reachable via DATABASE_URL):
    uv run python -m eval.run_eval [--save eval/results/<name>.json]
"""

import argparse
import asyncio
import json
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.llm import get_embedder, get_llm_client
from app.core.logging import setup_logging
from app.models import Job, JobSkill, Skill
from app.rag.search import search

CASES_PATH = Path(__file__).with_name("rag_queries.yaml")
K = 10


@dataclass
class CaseResult:
    query: str
    relevant: int
    recall: float
    precision: float
    hit_at_1: bool
    filters_ok: bool
    filter_errors: list[str]
    relaxed: list[str]


async def load_jobs(session: AsyncSession) -> list[dict[str, Any]]:
    jobs: dict[int, dict[str, Any]] = {
        job.id: {
            "id": job.id,
            "title": job.title,
            "city": job.location_city,
            "experience_min": job.experience_min,
            "employment_type": job.employment_type,
            "skills": set(),
        }
        for job in (await session.execute(select(Job).where(Job.is_active.is_(True)))).scalars()
    }
    rows = await session.execute(
        select(JobSkill.job_id, Skill.canonical_name).join(Skill, Skill.id == JobSkill.skill_id)
    )
    for job_id, name in rows.all():
        if job_id in jobs:
            jobs[job_id]["skills"].add(name)
    return list(jobs.values())


def is_relevant(job: dict[str, Any], rule: dict[str, Any]) -> bool:
    if "city" in rule and job["city"] != rule["city"]:
        return False
    if "employment_type" in rule and job["employment_type"] != rule["employment_type"]:
        return False
    if "experience_max" in rule and (job["experience_min"] or 0) > rule["experience_max"]:
        return False
    if "skills_any" in rule and not job["skills"] & set(rule["skills_any"]):
        return False
    title = job["title"].lower()
    return "title_any" not in rule or any(w.lower() in title for w in rule["title_any"])


def filter_errors(parsed: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    errors = []
    for key, want in expected.items():
        got = parsed.get(key)
        ok = set(want) <= set(got or []) if key == "skills" else got == want
        if not ok:
            errors.append(f"{key}: expected {want}, got {got}")
    return errors


async def run() -> dict[str, Any]:
    settings = get_settings()
    setup_logging("WARNING")
    client, embedder = get_llm_client(), get_embedder()
    if client is None:
        raise SystemExit("GEMINI_API_KEY is not set")
    cases = yaml.safe_load(CASES_PATH.read_text(encoding="utf-8"))

    results: list[CaseResult] = []
    async with SessionLocal() as session:
        jobs = await load_jobs(session)
        for case in cases:
            relevant = {j["id"] for j in jobs if is_relevant(j, case["relevant"])}
            response = await search(
                session, client, settings.gemini_parser_model, embedder, case["query"], K
            )
            top = [hit.job.id for hit in response.items]
            hits = len(relevant & set(top))
            errors = filter_errors(response.filters.model_dump(), case.get("expected", {}))
            results.append(
                CaseResult(
                    query=case["query"],
                    relevant=len(relevant),
                    recall=hits / min(len(relevant), K) if relevant else 0.0,
                    precision=hits / len(top) if top else 0.0,
                    hit_at_1=bool(top) and top[0] in relevant,
                    filters_ok=not errors,
                    filter_errors=errors,
                    relaxed=response.relaxed,
                )
            )

    for r in results:
        flag = "" if r.filters_ok else f"  filter: {'; '.join(r.filter_errors)}"
        relaxed = f"  relaxed: {r.relaxed}" if r.relaxed else ""
        print(
            f"R@{K} {r.recall:.2f} | P@{K} {r.precision:.2f} | top1 {'+' if r.hit_at_1 else '-'}"
            f" | rel {r.relevant:3d} | {r.query[:60]}{flag}{relaxed}"
        )
    summary = {
        "cases": len(results),
        f"recall@{K}": round(statistics.mean(r.recall for r in results), 3),
        f"precision@{K}": round(statistics.mean(r.precision for r in results), 3),
        "hit@1": round(statistics.mean(r.hit_at_1 for r in results), 3),
        "filter_accuracy": round(statistics.mean(r.filters_ok for r in results), 3),
        "relaxed_cases": sum(bool(r.relaxed) for r in results),
        "cases_without_relevant": sum(r.relevant == 0 for r in results),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return {"summary": summary, "cases": [asdict(r) for r in results]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", type=Path)
    save = parser.parse_args().save
    payload = asyncio.run(run())
    if save:
        save.parent.mkdir(parents=True, exist_ok=True)
        save.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
