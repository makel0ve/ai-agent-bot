from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.constants import MODELS
from app.database import async_session
from app.repositories.conversation import create_conversation
from app.repositories.user import get_user, update_provider

router_model = Router()


@router_model.message(Command("model"))
async def cmd_model(message: Message):
    async with async_session() as session:
        user = await get_user(session=session, telegram_id=message.from_user.id)
        current_model = user.preferred_provider

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"✅ {val}" if key == current_model else val,
                        callback_data=f"model:{key}",
                    )
                ]
                for key, val in MODELS.items()
            ]
        )

    await message.answer("Выбери модель:", reply_markup=keyboard)


@router_model.callback_query(F.data.startswith("model:"))
async def on_model_selected(callback: CallbackQuery):
    provider = callback.data.split(":")[1]

    async with async_session() as session:
        user = await get_user(session=session, telegram_id=callback.from_user.id)

        await update_provider(
            session=session,
            telegram_id=callback.from_user.id,
            preferred_provider=provider,
        )
        await create_conversation(session=session, user_id=user.id)
        await session.commit()

    await callback.message.edit_text(
        f"Модель изменена на: {provider}\nНачат новый диалог."
    )
    await callback.answer()
