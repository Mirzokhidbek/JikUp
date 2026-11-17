from collections.abc import Iterable, Mapping

from pydantic import BaseModel

REQUIRED_WEIGHT = 2
PREFERRED_WEIGHT = 1


class SkillGap(BaseModel):
    match_percent: int | None
    required_matched: list[str]
    required_missing: list[str]
    preferred_matched: list[str]
    preferred_missing: list[str]
    experience_required: int | None
    experience_years: float | None
    experience_gap: float | None


def compute_skill_gap(
    resume_skills: Iterable[str],
    job_skills: Mapping[str, bool],
    resume_years: float | None,
    job_experience_min: int | None,
) -> SkillGap:
    have = set(resume_skills)
    required = {name for name, is_required in job_skills.items() if is_required}
    preferred = set(job_skills) - required

    total = REQUIRED_WEIGHT * len(required) + PREFERRED_WEIGHT * len(preferred)
    earned = REQUIRED_WEIGHT * len(required & have) + PREFERRED_WEIGHT * len(preferred & have)
    gap = None
    if job_experience_min is not None and resume_years is not None:
        gap = round(max(job_experience_min - resume_years, 0.0), 1)

    return SkillGap(
        match_percent=round(100 * earned / total) if total else None,
        required_matched=sorted(required & have),
        required_missing=sorted(required - have),
        preferred_matched=sorted(preferred & have),
        preferred_missing=sorted(preferred - have),
        experience_required=job_experience_min,
        experience_years=resume_years,
        experience_gap=gap,
    )
