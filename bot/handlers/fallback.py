from aiogram import Router
from aiogram.types import CallbackQuery, Message

from bot import locales, ui
from bot.db import Database

router = Router(name="fallback")


@router.message()
async def cleanup(message: Message) -> None:
    """Стикеры, фото, неизвестные команды — удаляем, чтобы чат оставался чистым."""
    await ui.delete_incoming(message)


@router.callback_query()
async def stale_button(callback: CallbackQuery, db: Database) -> None:
    lang = (await db.get_user(callback.from_user.id)).lang
    await callback.answer(locales.get(lang)["t_stale"], show_alert=True)
