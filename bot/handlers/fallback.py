from aiogram import Router
from aiogram.types import CallbackQuery, Message

from bot import ui

router = Router(name="fallback")


@router.message()
async def cleanup(message: Message) -> None:
    """Стикеры, фото, неизвестные команды — удаляем, чтобы чат оставался чистым."""
    await ui.delete_incoming(message)


@router.callback_query()
async def stale_button(callback: CallbackQuery) -> None:
    await callback.answer("Кнопка устарела — отправьте /start", show_alert=True)
