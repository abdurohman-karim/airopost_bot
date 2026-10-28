from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot import locales, screens, texts, timeutil, ui
from bot.db import Database
from bot.keyboards import LangCb, Nav
from bot.services import WeatherService
from bot.states import Form

router = Router(name="navigation")


@router.callback_query(Nav.filter())
async def on_nav(
    callback: CallbackQuery,
    callback_data: Nav,
    bot: Bot,
    state: FSMContext,
    db: Database,
    weather: WeatherService,
) -> None:
    chat_id = callback.from_user.id
    message_id = callback.message.message_id if callback.message else None
    await ui.leave_location_mode(bot, state, chat_id)
    user = await db.get_user(chat_id)
    loc = locales.get(user.lang)
    screen, toast = callback_data.to, None

    if screen == "toggle":
        enabled = not user.notify_enabled
        fields = {"notify_enabled": enabled}
        if enabled:
            fields["last_sent"] = timeutil.last_sent_after_change(user.tz, user.notify_time)
        user = await db.update(chat_id, **fields)
        screen = "settings"
        toast = loc["t_on"] if enabled else loc["t_off"]
    elif screen == "time":
        await state.set_state(Form.time)

    text, markup = await screens.build(
        screen, user, weather,
        page=callback_data.page, fresh=callback_data.fresh, name=callback.from_user.first_name,
    )
    if callback_data.fresh and text != texts.error(user.lang):
        toast = loc["t_refreshed"]
    await ui.show(bot, db, chat_id, text, markup, message_id)
    if screen == "location":
        await ui.enter_location_mode(bot, state, chat_id, user.lang)
    await callback.answer(toast)


@router.callback_query(LangCb.filter())
async def on_lang(
    callback: CallbackQuery,
    callback_data: LangCb,
    bot: Bot,
    state: FSMContext,
    db: Database,
    weather: WeatherService,
) -> None:
    chat_id = callback.from_user.id
    await ui.leave_location_mode(bot, state, chat_id)
    user = await db.update(chat_id, lang=locales.get(callback_data.code).code)
    text, markup = await screens.build(callback_data.back, user, weather, name=callback.from_user.first_name)
    await ui.show(bot, db, chat_id, text, markup, callback.message.message_id if callback.message else None)
    await callback.answer(locales.get(user.lang)["t_lang"])
