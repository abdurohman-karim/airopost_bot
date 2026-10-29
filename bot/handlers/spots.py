"""Перевалы на автодорогах и горнолыжные курорты: погода на высоте перевала и наверху трасс."""
import asyncio

from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot import keyboards as kb
from bot import locales, texts, ui
from bot import spot_texts as st
from bot.catalog import PASSES, RESORTS
from bot.db import Database
from bot.keyboards import SpotCb
from bot.services import MountainForecast, MountainService, WeatherError

router = Router(name="spots")


async def _forecast(mountains: MountainService, lat: float, lon: float, ele: float) -> MountainForecast | None:
    try:
        return await mountains.forecast(lat, lon, ele)
    except WeatherError:
        return None


async def resort_forecasts(mountains: MountainService, lang: str) -> list[tuple[st.Resort, MountainForecast | None]]:
    items = st.resorts(lang, RESORTS)
    fcs = await asyncio.gather(*(_forecast(mountains, r.lat, r.lon, r.top) for r in items))
    return list(zip(items, fcs))


@router.callback_query(SpotCb.filter())
async def on_spot(
    callback: CallbackQuery, callback_data: SpotCb, bot: Bot, state: FSMContext, db: Database,
    mountains: MountainService,
) -> None:
    chat_id, message_id = callback.from_user.id, callback.message.message_id if callback.message else None
    lang = (await db.get_user(chat_id)).lang
    loc = locales.get(lang)
    action, key = callback_data.a, callback_data.k
    await ui.leave_location_mode(bot, state, chat_id)
    if action == "skisub":
        subscribed = await db.toggle_ski_sub(chat_id, key)
        await callback.answer(loc["t_ski_sub" if subscribed else "t_ski_unsub"], show_alert=subscribed)
    else:
        # Прогнозы грузятся несколько секунд — отвечаем на нажатие сразу, чтобы кнопка не «висела»
        await callback.answer()

    if action == "passes":
        items = st.passes(lang, PASSES)
        fcs = await asyncio.gather(*(_forecast(mountains, p.lat, p.lon, p.ele) for p in items))
        await ui.show(bot, db, chat_id, st.passes_list(lang, list(zip(items, fcs))), kb.passes(lang, items), message_id)
    elif action == "pass":
        p = next((x for x in st.passes(lang, PASSES) if x.key == key), None)
        fc = p and await _forecast(mountains, p.lat, p.lon, p.ele)
        if not fc:
            await ui.show(bot, db, chat_id, texts.error(lang), kb.pass_detail(lang, key), message_id)
            return
        await ui.show(bot, db, chat_id, st.pass_detail(lang, p, fc), kb.pass_detail(lang, key), message_id)
    elif action == "ski":
        items = await resort_forecasts(mountains, lang)
        await ui.show(bot, db, chat_id, st.ski_list(lang, items), kb.ski(lang, [r for r, _ in items]), message_id)
    elif action in ("resort", "skisub"):
        r = next((x for x in st.resorts(lang, RESORTS) if x.key == key), None)
        if not r:
            return
        fc = await _forecast(mountains, r.lat, r.lon, r.top)
        subscribed = key in await db.ski_subs(chat_id)
        if not fc:
            await ui.show(bot, db, chat_id, texts.error(lang), kb.resort(lang, key, subscribed), message_id)
        else:
            await ui.show(bot, db, chat_id, st.resort_detail(lang, r, fc, subscribed), kb.resort(lang, key, subscribed),
                          message_id)
