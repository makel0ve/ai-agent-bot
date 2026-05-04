from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router_help = Router()


@router_help.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Я — AI-ассистент с инструментами.\n\n"
        "Что я умею:\n"
        "- Искать информацию в интернете\n"
        "- Показывать погоду и прогноз\n"
        "- Конвертировать валюты\n"
        "- Сохранять и показывать заметки\n\n"
        "Команды:\n"
        "/new — начать новый диалог\n"
        "/model — выбрать модель\n"
        "/notes - все заметки\n"
        "/stats - статистика пользователя\n"
        "/help — эта справка"
    )
