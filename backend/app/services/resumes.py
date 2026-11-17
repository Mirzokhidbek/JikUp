import uuid

from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Resume
from app.resumes.parser import ParsedResume
from app.schemas.resume import ResumeOut


def _out(resume: Resume) -> ResumeOut:
    return ResumeOut(
        id=resume.id,
        filename=resume.filename,
        expires_at=resume.expires_at,
        parsed=ParsedResume.model_validate(resume.parsed or {}),
    )


async def create_resume(
    session: AsyncSession, filename: str, text: str, parsed: ParsedResume
) -> ResumeOut:
    resume = (
        await session.execute(
            insert(Resume)
            .values(filename=filename, raw_text=text, parsed=parsed.model_dump())
            .returning(Resume)
        )
    ).scalar_one()
    await session.commit()
    return _out(resume)


async def get_resume_row(session: AsyncSession, resume_id: uuid.UUID) -> Resume | None:
    return (
        await session.execute(
            select(Resume).where(Resume.id == resume_id, Resume.expires_at > func.now())
        )
    ).scalar_one_or_none()


async def get_resume(session: AsyncSession, resume_id: uuid.UUID) -> ResumeOut | None:
    resume = await get_resume_row(session, resume_id)
    return _out(resume) if resume else None


async def delete_resume(session: AsyncSession, resume_id: uuid.UUID) -> bool:
    result = await session.execute(
        delete(Resume).where(Resume.id == resume_id).returning(Resume.id)
    )
    await session.commit()
    return result.scalar_one_or_none() is not None


async def purge_expired(session: AsyncSession) -> int:
    result = await session.execute(
        delete(Resume).where(Resume.expires_at <= func.now()).returning(Resume.id)
    )
    await session.commit()
    return len(result.all())
