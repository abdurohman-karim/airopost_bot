from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import keyboards as kb
from bot import texts, timeutil, ui
from bot.db import Database, User
from bot.keyboards import TimeCb
from bot.states import Form

router = Router(name="schedule")


async def _set_time(db: Database, chat_id: int, value: str) -> User:
    user = await db.get_user(chat_id)
    return await db.update(
        chat_id, notify_time=value, last_sent=timeutil.last_sent_after_change(user.tz, value)
    )


@router.callback_query(TimeCb.filter())
async def on_time(callback: CallbackQuery, callback_data: TimeCb, bot: Bot, state: FSMContext, db: Database) -> None:
    chat_id = callback.from_user.id
    message_id = callback.message.message_id if callback.message else None
    await ui.leave_location_mode(bot, state, chat_id)

    if callback_data.minute < 0:
        await state.set_state(Form.time)
        hour = callback_data.hour
        await ui.show(bot, db, chat_id, texts.time_minutes(hour), kb.time_minutes(hour), message_id)
        await callback.answer()
        return

    value = f"{callback_data.hour:02d}:{callback_data.minute:02d}"
    user = await _set_time(db, chat_id, value)
    await ui.show(bot, db, chat_id, texts.settings(user), kb.settings(user), message_id)
    await callback.answer(f"✅ Сводка будет приходить в {value}")


@router.message(Form.time, F.text)
async def on_time_text(message: Message, bot: Bot, state: FSMContext, db: Database) -> None:
    chat_id = message.chat.id
    await ui.delete_incoming(message)
    value = timeutil.parse_time(message.text)
    if not value:
        user = await db.get_user(chat_id)
        await ui.show(bot, db, chat_id, texts.time_hours(user, error=True), kb.time_hours(user))
        return
    await state.clear()
    user = await _set_time(db, chat_id, value)
    text = f"✅ Сводка будет приходить в <b>{value}</b>\n\n" + texts.settings(user)
    await ui.show(bot, db, chat_id, text, kb.settings(user))
