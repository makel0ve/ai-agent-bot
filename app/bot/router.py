from aiogram import Router

from app.bot.handlers.conversation import router_conversation
from app.bot.handlers.help import router_help
from app.bot.handlers.message import router_message
from app.bot.handlers.model import router_model
from app.bot.handlers.notes import router_notes
from app.bot.handlers.start import router_start
from app.bot.handlers.stats import router_stats

main_router = Router()


main_router.include_router(router_start)
main_router.include_router(router_stats)
main_router.include_router(router_help)
main_router.include_router(router_model)
main_router.include_router(router_notes)
main_router.include_router(router_conversation)
main_router.include_router(router_message)
