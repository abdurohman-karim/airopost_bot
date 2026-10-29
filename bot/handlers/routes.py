"""GPX-маршруты: пользователь присылает трек, бот считает длину, набор и время в пути и показывает
погоду в точках трека на то время, когда человек будет там проходить."""
import asyncio
import io
import logging
from datetime import datetime, timedelta

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import gpx, locales, texts, ui, weekend
from bot import keyboards as kb
from bot import route_texts as rt
from bot.db import Database
from bot.keyboards import RouteCb
from bot.services import MountainForecast, MountainService, WeatherError
from bot.services.models import get_tz

log = logging.getLogger(__name__)
router = Router(name="routes")

PARALLEL = 4
ELEVATION_CHUNK = 100     # столько точек за запрос к Open-Meteo Elevation


async def _list(db: Database, chat_id: int, lang: str):
    items = await db.routes(chat_id)
    return rt.routes_list(lang, bool(items)), kb.routes(lang, items)


@router.message(F.document.file_name.lower().endswith(".gpx"))
async def on_gpx(message: Message, bot: Bot, state: FSMContext, db: Database, mountains: MountainService) -> None:
    """GPX принимается в любой момент — достаточно прислать файл боту."""
    chat_id = message.chat.id
    lang = (await db.get_user(chat_id)).lang
    await ui.leave_location_mode(bot, state, chat_id)
    doc = message.document
    await ui.delete_incoming(message)
    if (doc.file_size or 0) > gpx.MAX_FILE:
        text, markup = await _list(db, chat_id, lang)
        await ui.show(bot, db, chat_id, locales.get(lang)["rt_too_big"] + "\n\n" + text, markup)
        return
    await ui.show(bot, db, chat_id, rt.reading(lang))
    try:
        buffer = io.BytesIO()
        await bot.download(doc, destination=buffer)
        name, points = gpx.parse(buffer.getvalue(), doc.file_name.rsplit(".", 1)[0])
        points = await _with_elevation(mountains, points)
    except (gpx.GpxError, TelegramAPIError, WeatherError) as e:
        log.info("GPX от %s не прочитан: %s", chat_id, e)
        text, markup = await _list(db, chat_id, lang)
        await ui.show(bot, db, chat_id, locales.get(lang)["rt_bad"] + "\n\n" + text, markup)
        return
    route_id = await db.add_route(chat_id, name, points)
    await _open(bot, db, mountains, chat_id, lang, route_id)


async def _with_elevation(mountains: MountainService, points: list) -> list[list[float]]:
    """Высоты из трека. Отдельные пропуски заполняем между соседними точками — смешивать GPS и модель
    рельефа нельзя, иначе набор высоты раздувается. Если высот в треке почти нет — берём модель для всех."""
    filled = [list(p) for p in points]
    known = [i for i, p in enumerate(points) if p[2] is not None]
    if len(known) >= len(points) / 2:
        for i, p in enumerate(filled):
            if p[2] is not None:
                continue
            before = max((k for k in known if k < i), default=None)
            after = min((k for k in known if k > i), default=None)
            if before is None or after is None:
                p[2] = points[before if after is None else after][2]
            else:
                p[2] = points[before][2] + (points[after][2] - points[before][2]) * (i - before) / (after - before)
    else:
        for start in range(0, len(points), ELEVATION_CHUNK):
            chunk = points[start:start + ELEVATION_CHUNK]
            values = await mountains.elevations([(p[0], p[1]) for p in chunk])
            for j, value in enumerate(values):
                filled[start + j][2] = value or 0.0
    return [[round(lat, 6), round(lon, 6), round(ele, 1)] for lat, lon, ele in filled]


async def _start_forecast(mountains: MountainService, tr: gpx.Track) -> MountainForecast | None:
    first = tr.legs[0]
    try:
        return await mountains.forecast(first.lat, first.lon, first.ele)
    except WeatherError:
        return None


async def _open(bot: Bot, db: Database, mountains: MountainService, chat_id: int, lang: str, route_id: int,
                message_id: int | None = None) -> None:
    stored = await db.route(chat_id, route_id)
    if not stored:
        await ui.show(bot, db, chat_id, *await _list(db, chat_id, lang), message_id)
        return
    tr = gpx.track(*stored)
    fc = await _start_forecast(mountains, tr)
    now = fc.local_now() if fc else datetime.now(get_tz(weekend.DEFAULT_TZ)).replace(tzinfo=None)
    loc = locales.get(lang)
    options = [(code, rt.start_label(loc, code, dt)) for code, dt in gpx.start_options(now)]
    await ui.show(bot, db, chat_id, rt.summary(lang, tr), kb.route_start(lang, route_id, options), message_id)


async def _plan(mountains: MountainService, tr: gpx.Track, start: datetime) -> list[rt.Stop]:
    semaphore = asyncio.Semaphore(PARALLEL)

    async def one(leg: gpx.Leg) -> rt.Stop:
        at = start + timedelta(hours=leg.hours)
        async with semaphore:
            try:
                fc = await mountains.forecast(leg.lat, leg.lon, leg.ele)
            except WeatherError:
                return rt.Stop(leg, at, None, False)
        hour = at.replace(minute=0, second=0, microsecond=0)
        row = next((h for h in fc.hourly if h["time"] == hour), None)
        if row is None:
            return rt.Stop(leg, at, None, False)
        return rt.Stop(leg, at, fc.at(row, leg.ele), fc.thunder(row))

    return list(await asyncio.gather(*(one(leg) for leg in tr.checkpoints())))


@router.callback_query(RouteCb.filter())
async def on_route(
    callback: CallbackQuery, callback_data: RouteCb, bot: Bot, state: FSMContext, db: Database,
    mountains: MountainService,
) -> None:
    chat_id, message_id = callback.from_user.id, callback.message.message_id if callback.message else None
    lang = (await db.get_user(chat_id)).lang
    await ui.leave_location_mode(bot, state, chat_id)
    await callback.answer()
    action = callback_data.a
    if action == "list":
        await ui.show(bot, db, chat_id, *await _list(db, chat_id, lang), message_id)
        return
    if action == "del":
        await db.delete_route(chat_id, callback_data.id)
        await ui.show(bot, db, chat_id, *await _list(db, chat_id, lang), message_id)
        return
    if action == "open":
        await _open(bot, db, mountains, chat_id, lang, callback_data.id, message_id)
        return

    stored = await db.route(chat_id, callback_data.id)
    if not stored:
        await ui.show(bot, db, chat_id, *await _list(db, chat_id, lang), message_id)
        return
    tr = gpx.track(*stored)
    fc = await _start_forecast(mountains, tr)
    if not fc:
        await ui.show(bot, db, chat_id, texts.error(lang), kb.route_plan(lang, callback_data.id), message_id)
        return
    start = dict(gpx.start_options(fc.local_now())).get(callback_data.s, fc.local_now())
    await ui.show(bot, db, chat_id, rt.reading(lang), None, message_id)
    stops = await _plan(mountains, tr, start)
    finish = start + timedelta(hours=tr.hours)
    day = fc.day(finish.date())
    sunset = day.get("sunset") if day else None
    await ui.show(bot, db, chat_id, rt.plan(lang, tr, stops, sunset), kb.route_plan(lang, callback_data.id), message_id)
