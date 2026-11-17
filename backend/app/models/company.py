from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    name_normalized: Mapped[str] = mapped_column(unique=True)
    industry: Mapped[str | None]
    size: Mapped[str | None]
    location: Mapped[str | None]
