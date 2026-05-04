from aiogram import BaseMiddleware
from aiogram.types import Message

from app.config import get_settings
from app.database import redis_client


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self):
        self._settings = get_settings()

    async def __call__(self, handler, event: Message, data: dict):
        telegram_id = event.from_user.id
        key = f"rate_limit:{telegram_id}"

        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, self._settings.rate_limit_window)

        if count > self._settings.rate_limit_requests:
            await event.answer("Ты превысил лимит запросов, подожди немного")
            return

        return await handler(event, data)
