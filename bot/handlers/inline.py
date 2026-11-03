"""Inline-режим: «@бот Чимган» в любом чате — карточка вершины с прогнозом и кнопками «Иду» / «Думаю».
Бота не нужно добавлять в группу: карточка — inline-сообщение, бот правит его по нажатиям."""
import asyncio
import logging

from aiogram import Bot, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot import keyboards as kb
from bot import links, locales
from bot import mountain_texts as mt
from bot.db import Database, Peak
from bot.keyboards import HikeCb
from bot.services import MountainForecast, MountainService, WeatherError

log = logging.getLogger(__name__)
router = Router(name="inline")

RESULTS = 8
INLINE_WAIT = 5           # с: Telegram ждёт ответа на inline-запрос недолго — без прогноза карточка всё равно уйдёт


def hike_key(peak: Peak) -> str | None:
    if peak.public:
        return f"c{peak.catalog_id}"
    return f"s{peak.token}" if peak.token else None


async def _peak_by_key(db: Database, key: str, lang: str) -> Peak | None:
    if key[:1] == "c" and key[1:].isdigit():
        return await db.catalog_peak(int(key[1:]), lang)
    if key[:1] == "s":
        found = await db.shared_peak(key[1:])
        return found[1] if found else None
    return None


async def _forecast(mountains: MountainService, peak: Peak, wait: float | None = None) -> MountainForecast | None:
    try:
        return await asyncio.wait_for(mountains.forecast(peak.lat, peak.lon, peak.ele), wait)
    except (WeatherError, asyncio.TimeoutError):
        return None


@router.inline_query()
async def on_inline(query: InlineQuery, bot: Bot, db: Database, mountains: MountainService) -> None:
    user = await db.get_user(query.from_user.id)
    lang = user.lang
    text = " ".join(query.query.split())[:64]
    own = [p for p in await db.peaks(query.from_user.id) if text.casefold() in p.name.casefold()]
    peaks = (own + await db.search_catalog(text, lang, RESULTS))[:RESULTS]
    forecasts = await asyncio.gather(*(_forecast(mountains, p, INLINE_WAIT) for p in peaks))
    bot_name = f"@{(await bot.me()).username}"
    results = []
    for peak, fc in zip(peaks, forecasts):
        key = hike_key(peak)
        if not key:
            continue
        results.append(InlineQueryResultArticle(
            id=key,
            title=f"⛰ {peak.name} · {peak.ele} {locales.get(lang)['m']}",
            description=mt.hike_description(lang, fc),
            input_message_content=InputTextMessageContent(message_text=mt.hike_card(lang, peak, fc, [], bot_name)),
            reply_markup=kb.hike(lang, key, links.peak_link(peak)),
        ))
    # Личные вершины в выдаче — результат свой у каждого пользователя
    await query.answer(results, cache_time=300, is_personal=True)


@router.callback_query(HikeCb.filter())
async def on_hike(callback: CallbackQuery, callback_data: HikeCb, bot: Bot, db: Database, mountains: MountainService) -> None:
    # Подсказки — на языке нажавшего, сама карточка — на языке того, кто её отправил
    loc = locales.get((await db.get_user(callback.from_user.id)).lang)
    lang = locales.get(callback_data.l).code
    message_id = callback.inline_message_id
    peak = await _peak_by_key(db, callback_data.k, lang)
    if not message_id or not peak:
        await callback.answer(loc["t_m_missing"], show_alert=True)
        return
    toast = None
    if callback_data.a in ("go", "maybe"):
        marked = await db.set_hike_status(message_id, callback.from_user.id, callback.from_user.full_name, callback_data.a)
        toast = loc[f"t_hike_{callback_data.a}"] if marked else loc["t_hike_off"]
    await callback.answer(toast)
    fc = await _forecast(mountains, peak)
    text = mt.hike_card(lang, peak, fc, await db.hike_people(message_id), f"@{(await bot.me()).username}")
    try:
        await bot.edit_message_text(text=text, inline_message_id=message_id,
                                    reply_markup=kb.hike(lang, callback_data.k, links.peak_link(peak)))
    except TelegramAPIError as e:
        if "not modified" not in str(e):
            log.info("Карточку похода %s не обновить: %s", message_id, e)
