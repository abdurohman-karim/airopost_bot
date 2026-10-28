"""Чистый чат.

У каждого пользователя есть одно «живое» сообщение бота (users.menu_msg_id).
Все экраны показываются редактированием этого сообщения. Новое сообщение
отправляется только когда без этого нельзя (/start, ежедневная сводка, старое
сообщение удалено) — и тогда предыдущее удаляется, чтобы наверху не оставалось
старых меню. Сообщения пользователя (текст, геолокация) бот удаляет сразу после обработки.
"""
from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardRemove

from bot import keyboards as kb
from bot import texts
from bot.db import Database
from bot.states import Form

log = logging.getLogger(__name__)


async def delete_message(bot: Bot, chat_id: int, message_id: int | None) -> bool:
    if not message_id:
        return False
    try:
        await bot.delete_message(chat_id, message_id)
        return True
    except TelegramAPIError:
        pass
    # Сообщения старше 48 часов Telegram удалить не даёт — хотя бы убираем с них кнопки
    try:
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
    except TelegramAPIError:
        pass
    return False


async def delete_incoming(message: Message) -> None:
    """Удалить сообщение пользователя — в чате остаётся только живое сообщение бота."""
    try:
        await message.delete()
    except TelegramAPIError:
        pass


async def _edit(bot: Bot, chat_id: int, message_id: int, text: str, markup: InlineKeyboardMarkup | None) -> bool:
    try:
        await bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
        return True
    except TelegramBadRequest as e:
        if "message is not modified" in e.message:
            return True
        log.debug("Не удалось отредактировать %s/%s: %s", chat_id, message_id, e.message)
        return False


async def show(
    bot: Bot,
    db: Database,
    chat_id: int,
    text: str,
    markup: InlineKeyboardMarkup | None = None,
    message_id: int | None = None,
) -> int:
    """Показать экран в живом сообщении. message_id — сообщение, на котором нажали кнопку."""
    user = await db.get_user(chat_id)
    target = message_id or user.menu_msg_id
    if target and await _edit(bot, chat_id, target, text, markup):
        if target != user.menu_msg_id:
            # Нажали кнопку на другом сообщении — теперь живое оно, прежнее убираем
            await delete_message(bot, chat_id, user.menu_msg_id)
            await db.update(chat_id, menu_msg_id=target)
        return target
    return await send_fresh(bot, db, chat_id, text, markup)


async def send_fresh(
    bot: Bot,
    db: Database,
    chat_id: int,
    text: str,
    markup: InlineKeyboardMarkup | None = None,
) -> int:
    """Отправить экран новым сообщением внизу чата и удалить предыдущее живое сообщение."""
    user = await db.get_user(chat_id)
    message = await bot.send_message(chat_id, text, reply_markup=markup)
    if user.menu_msg_id and user.menu_msg_id != message.message_id:
        await delete_message(bot, chat_id, user.menu_msg_id)
    await db.update(chat_id, menu_msg_id=message.message_id)
    return message.message_id


async def enter_location_mode(bot: Bot, state: FSMContext, chat_id: int) -> None:
    """Кнопку «Отправить геолокацию» умеет только обычная (не inline) клавиатура,
    поэтому на время выбора под живым сообщением появляется подсказка с ней."""
    await leave_location_mode(bot, state, chat_id)
    message = await bot.send_message(chat_id, texts.LOCATION_KEYBOARD_HINT, reply_markup=kb.location_reply())
    await state.set_state(Form.location)
    await state.update_data(prompt_id=message.message_id)


async def leave_location_mode(bot: Bot, state: FSMContext, chat_id: int) -> None:
    """Сбросить состояние и убрать подсказку с клавиатурой геолокации, если она есть."""
    prompt_id = (await state.get_data()).get("prompt_id")
    await state.clear()
    if not prompt_id:
        return
    await delete_message(bot, chat_id, prompt_id)
    # Некоторые клиенты оставляют клавиатуру и после удаления сообщения — убираем её явно
    try:
        message = await bot.send_message(
            chat_id, "⌛", reply_markup=ReplyKeyboardRemove(), disable_notification=True
        )
        await delete_message(bot, chat_id, message.message_id)
    except TelegramAPIError:
        pass
