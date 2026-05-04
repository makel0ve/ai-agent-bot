from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None = None,
    preferred_provider: str = "gigachat",
):
    user = User(
        telegram_id=telegram_id,
        username=username,
        preferred_provider=preferred_provider,
    )
    session.add(user)
    await session.flush()

    return user


async def get_user(session: AsyncSession, telegram_id: int):
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))

    user = result.scalar_one_or_none()

    return user


async def update_provider(
    session: AsyncSession, telegram_id: int, preferred_provider: str
):
    await session.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(preferred_provider=preferred_provider)
    )
