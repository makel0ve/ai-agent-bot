from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import async_session
from app.repositories.conversation import create_conversation
from app.repositories.user import get_user

router_conversation = Router()


@router_conversation.message(Command("new"))
async def cmd_new(message: Message):
    async with async_session() as session:
        user = await get_user(session=session, telegram_id=message.from_user.id)

        _ = await create_conversation(session=session, user_id=user.id)

        await session.commit()

    await message.answer("Начат новый диалог!")
