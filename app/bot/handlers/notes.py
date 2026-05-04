from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import async_session
from app.repositories.user import get_user
from app.tools.notes import ListNoteTool

router_notes = Router()


@router_notes.message(Command("notes"))
async def cmd_notes(message: Message):
    async with async_session() as session:
        user = await get_user(session=session, telegram_id=message.from_user.id)
        tool = ListNoteTool(session=session, user_id=user.id)
        result = await tool.execute()

    await message.answer(result)
