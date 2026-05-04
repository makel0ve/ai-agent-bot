import asyncio

from aiogram.exceptions import TelegramBadRequest


class MessageUpdater:
    def __init__(self, message, interval: float = 1.0):
        self._message = message
        self._interval = interval
        self._current_text: str = ""
        self._last_sent: str = ""
        self._task: asyncio.Task | None = None
        self._parse_mode: str | None = None

    async def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._loop())

    def update(self, text: str, parse_mode: str | None = None):
        self._current_text = text
        self._parse_mode = parse_mode

    async def flush(self):
        if self._task:
            self._task.cancel()

        await self._message.edit_text(self._current_text, parse_mode=self._parse_mode)

    async def _loop(self):
        while True:
            await asyncio.sleep(self._interval)

            try:
                if self._current_text != self._last_sent:
                    await self._message.edit_text(
                        self._current_text, parse_mode=self._parse_mode
                    )
                    self._last_sent = self._current_text

            except TelegramBadRequest:
                pass
