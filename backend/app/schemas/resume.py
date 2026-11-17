import uuid
from datetime import datetime

from pydantic import BaseModel

from app.resumes.parser import ParsedResume


class ResumeOut(BaseModel):
    id: uuid.UUID
    filename: str
    expires_at: datetime
    parsed: ParsedResume
