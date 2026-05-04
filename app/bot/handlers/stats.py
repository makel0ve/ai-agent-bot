from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.constants import MODELS
from app.database import async_session
from app.repositories.message import get_user_message_counts
from app.repositories.note import get_notes_count
from app.repositories.user import get_user

router_stats = Router()


@router_stats.message(Command("stats"))
async def cmd_stats(message: Message):
    async with async_session() as session:
        user = await get_user(session=session, telegram_id=message.from_user.id)
        total_notes = await get_notes_count(session=session, user_id=user.id)
        total_messages, tool_calls = await get_user_message_counts(
            session=session, user_id=user.id
        )

    text = (
        "📊 Твоя статистика\n\n"
        f"🤖 Провайдер: {MODELS.get(user.preferred_provider)}\n"
        f"💬 Сообщений: {total_messages}\n"
        f"🔧 Tool calls: {tool_calls}\n"
        f"📝 Заметок: {total_notes}\n"
        f"📅 С нами с: {user.created_at.strftime('%d.%m.%Y')}\n"
    )

    await message.answer(text=text)
