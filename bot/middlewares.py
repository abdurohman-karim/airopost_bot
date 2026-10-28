from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot import locales
from bot.db import Database


class UserMiddleware(BaseMiddleware):
    """Заводит пользователя при первом сообщении или нажатии, язык — из настроек Telegram."""

    def __init__(self, db: Database) -> None:
        self.db = db

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user and not user.is_bot:
            await self.db.ensure_user(user.id, locales.detect(user.language_code))
        return await handler(event, data)
