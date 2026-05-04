from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.database import async_session
from app.repositories.user import create_user, get_user

router_start = Router()


@router_start.message(CommandStart())
async def cmd_start(message: Message):
    async with async_session() as session:
        user = await get_user(session=session, telegram_id=message.from_user.id)

        if not user:
            user = await create_user(
                session=session,
                telegram_id=message.from_user.id,
                username=message.from_user.username,
            )

        await session.commit()

    await message.answer(
        f"Привет, {message.from_user.first_name}!\n"
        f"У тебя выбрана модель: {user.preferred_provider}"
    )
