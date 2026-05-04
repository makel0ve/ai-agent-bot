import asyncio
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI

from app.bot.middleware import RateLimitMiddleware
from app.bot.router import main_router
from app.config import get_settings

settings = get_settings()


bot = Bot(token=settings.telegram_token.get_secret_value())
dp = Dispatcher()
dp.include_router(main_router)
dp.message.middleware(RateLimitMiddleware())


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.webhook_url:
        await bot.set_webhook(
            url=f"{settings.webhook_url}/webhook/{settings.telegram_token.get_secret_value()}"
        )
    
    else:
        polling_task = asyncio.create_task(dp.start_polling(bot))

    yield

    if settings.webhook_url:
        await bot.delete_webhook()
    
    else:
        polling_task.cancel()


app = FastAPI(lifespan=lifespan)


@app.post("/webhook/{token}")
async def webhook(token: str, update: dict):
    if token != settings.telegram_token.get_secret_value():
        return {"error": "unauthorized"}

    telegram_update = Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)
