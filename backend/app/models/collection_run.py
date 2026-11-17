from datetime import datetime

from sqlalchemy import func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CollectionRun(Base):
    __tablename__ = "collection_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str]
    started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    finished_at: Mapped[datetime | None]
    fetched: Mapped[int] = mapped_column(server_default=text("0"))
    inserted: Mapped[int] = mapped_column(server_default=text("0"))
    updated: Mapped[int] = mapped_column(server_default=text("0"))
    errors: Mapped[int] = mapped_column(server_default=text("0"))
