from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser
from app.core.passwords import hash_password, verify_password
from app.models import User


class EmailTaken(Exception):
    pass


async def create_user(session: AsyncSession, email: str, password: str) -> CurrentUser:
    try:
        user_id = (
            await session.execute(
                insert(User)
                .values(email=email, password_hash=hash_password(password))
                .returning(User.id)
            )
        ).scalar_one()
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise EmailTaken from None
    return CurrentUser(id=user_id, email=email)


async def authenticate(session: AsyncSession, email: str, password: str) -> CurrentUser | None:
    user = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not verify_password(user.password_hash if user else None, password) or user is None:
        return None
    return CurrentUser(id=user.id, email=user.email)
