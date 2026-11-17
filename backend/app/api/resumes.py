import asyncio
import logging
import uuid
from pathlib import PurePath
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.llm import LLM
from app.resumes.parser import parse_resume
from app.resumes.pdf import MAX_BYTES, ResumeFileError, extract_text
from app.schemas.resume import ResumeOut
from app.services.resumes import create_resume, delete_resume, get_resume

router = APIRouter(prefix="/resumes", tags=["resumes"])
log = logging.getLogger(__name__)

Session = Annotated[AsyncSession, Depends(get_session)]
MAX_FILENAME = 200


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile, session: Session, client: LLM) -> ResumeOut:
    data = await file.read(MAX_BYTES + 1)
    try:
        text = await asyncio.to_thread(extract_text, data)
    except ResumeFileError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from None
    try:
        parsed = await parse_resume(client, get_settings().gemini_chat_model, text)
    except Exception as exc:
        log.warning("resume parsing failed (%s)", type(exc).__name__)
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Could not analyze the resume") from None
    filename = PurePath(file.filename or "resume.pdf").name[:MAX_FILENAME]
    return await create_resume(session, filename, text, parsed)


@router.get("/{resume_id}")
async def read_resume(resume_id: uuid.UUID, session: Session) -> ResumeOut:
    resume = await get_resume(session, resume_id)
    if resume is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_resume(resume_id: uuid.UUID, session: Session) -> Response:
    if not await delete_resume(session, resume_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
