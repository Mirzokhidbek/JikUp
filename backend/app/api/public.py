from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics import queries
from app.analytics.schemas import PublicStats
from app.core.db import get_session

CACHE_SECONDS = 300
TOP_SKILLS = 12

router = APIRouter(prefix="/public", tags=["public"])
Session = Annotated[AsyncSession, Depends(get_session)]


@router.get("/stats")
async def stats(session: Session, response: Response) -> PublicStats:
    """Market numbers for the landing page; aggregate only, no sign-in needed."""
    response.headers["Cache-Control"] = f"public, max-age={CACHE_SECONDS}"
    return await queries.public_stats(session, TOP_SKILLS)
