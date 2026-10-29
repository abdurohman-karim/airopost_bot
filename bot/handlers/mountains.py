import asyncio
import re
import time

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from bot import gear, links, locales, texts, timeutil, ui, weekend
from bot import keyboards as kb
from bot import mountain_texts as mt
from bot.catalog import REGIONS
from bot.coords import parse_coords
from bot.db import MAX_PEAKS, MAX_SUBS, Database, Peak, User
from bot.handlers.admin import notify_admins, tg_author
from bot.keyboards import GearCb, MCb, PeakPickCb
from bot.services import MountainService, PeakResult, WeatherError, WeatherService
from bot.states import Form

router = Router(name="mountains")

_ELEVATION_RE = re.compile(r"^\s*(\d{2,4}(?:[.,]\d+)?)\s*(?:m|м|metr|meters?)?\s*$", re.IGNORECASE)
SOS_FRESH_HOURS = 12      # точка с маршрута старше — для спасателей уже не годится
SOS_LOOKUP_SECONDS = 8    # высоту и ближайшее место ждём недолго: координаты важнее
SAME_PLACE = 0.004        # ~400 м — та же вершина
LIVE_ROUTE_SECONDS = 10 * 60   # трансляция геопозиции: экран маршрута обновляем не чаще
LIVE_SOS_SECONDS = 60


async def _delete_unless_live(message: Message) -> None:
    """Сообщение с трансляцией геопозиции не удаляем — иначе трансляция остановится."""
    if not (message.location and message.location.live_period):
        await ui.delete_incoming(message)


def _message_id(callback: CallbackQuery) -> int | None:
    return callback.message.message_id if callback.message else None


async def _list_screen(db: Database, chat_id: int, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    peaks = await db.peaks(chat_id)
    catalog = await db.catalog(lang)
    trip = await db.active_trip(chat_id)
    return mt.mountains(lang, peaks), kb.mountains(lang, peaks, len(peaks) < MAX_PEAKS, len(catalog), trip)


list_screen = _list_screen


async def peak_screen(
    db: Database, chat_id: int, lang: str, peak: Peak, mountains: MountainService, admins: frozenset[int],
    header: str | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    return await _peak_screen(db, chat_id, "open", lang, peak, mountains, admins, header=header)


async def _catalog_screen(db: Database, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    peaks = await db.catalog(lang)
    return mt.catalog(lang, peaks), kb.catalog(lang, mt.catalog_regions(peaks))


async def _region_screen(db: Database, lang: str, region_id: int, page: int) -> tuple[str, InlineKeyboardMarkup]:
    region = REGIONS[region_id] if 0 <= region_id < len(REGIONS) else REGIONS[0]
    peaks = mt.region_peaks(await db.catalog(lang), region)
    pages = mt.catalog_pages(peaks)
    page = min(max(page, 0), pages - 1)
    chunk = peaks[page * mt.CATALOG_PER_PAGE:(page + 1) * mt.CATALOG_PER_PAGE]
    return mt.catalog_region(lang, region, peaks, page), kb.catalog_region(lang, region, chunk, page, pages)


async def _peak_screen(
    db: Database,
    chat_id: int,
    action: str,
    lang: str,
    peak: Peak,
    mountains: MountainService,
    admins: frozenset[int] = frozenset(),
    page: int = 0,
    fresh: bool = False,
    header: str | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    try:
        fc = await mountains.forecast(peak.lat, peak.lon, peak.ele, fresh)
    except WeatherError:
        return texts.error(lang), kb.peak_error(lang, peak.id)
    if action == "profile":
        step = min(max(page, 0), mt.PROFILE_STEPS)
        return mt.profile(lang, peak, fc, step), kb.peak_profile(lang, peak.id, step, mt.PROFILE_STEPS)
    if action == "hourly":
        pages = mt.hourly_pages(fc)
        page = min(max(page, 0), pages - 1)
        return mt.hourly(lang, peak, fc, page), kb.peak_hourly(lang, peak.id, page, pages)
    if action == "outlook":
        return mt.outlook(lang, peak, fc), kb.peak_back(lang, peak.id)
    return mt.peak(lang, peak, fc, header), await _peak_keyboard(db, chat_id, lang, peak, admins)


async def _peak_keyboard(
    db: Database, chat_id: int, lang: str, peak: Peak, admins: frozenset[int],
) -> InlineKeyboardMarkup:
    link = links.peak_link(peak)
    share_url = links.share(link, mt.share_text(lang, peak)) if link else None
    subscribed = peak.id in await db.subscriptions(chat_id)
    # Публиковать можно, только если в боте настроен хотя бы один админ
    return kb.peak(lang, peak, can_publish=bool(admins), subscribed=subscribed, share_url=share_url)


async def _add_and_open(
    bot: Bot,
    db: Database,
    mountains: MountainService,
    admins: frozenset[int],
    chat_id: int,
    lang: str,
    name: str,
    lat: float,
    lon: float,
    ele: float,
    from_pin: bool = False,
    snapped: bool = False,
    message_id: int | None = None,
) -> None:
    loc = locales.get(lang)
    if len(await db.peaks(chat_id)) >= MAX_PEAKS:
        text, markup = await _list_screen(db, chat_id, lang)
        await ui.show(bot, db, chat_id, loc("t_m_limit", n=MAX_PEAKS) + "\n\n" + text, markup, message_id)
        return
    peak = await db.add_peak(chat_id, name, lat, lon, ele)
    header = loc["t_m_added"]
    if snapped:
        header += "\n" + loc["m_snapped"]
    elif from_pin:
        header += "\n" + loc("m_pin_hint", ele=peak.ele)
    text, markup = await _peak_screen(db, chat_id, "open", lang, peak, mountains, admins, header=header)
    await ui.show(bot, db, chat_id, text, markup, message_id)


# Действия, которые меняют вершину, — только для своих, не для каталога
OWNER_ACTIONS = {"edit", "del", "del_yes", "pub", "pub_yes"}


@router.callback_query(MCb.filter())
async def on_mountain(
    callback: CallbackQuery,
    callback_data: MCb,
    bot: Bot,
    state: FSMContext,
    db: Database,
    weather: WeatherService,
    mountains: MountainService,
    admins: frozenset[int],
) -> None:
    chat_id = callback.from_user.id
    message_id = _message_id(callback)
    lang = (await db.get_user(chat_id)).lang
    loc = locales.get(lang)
    action, toast = callback_data.a, None
    await ui.leave_location_mode(bot, state, chat_id)

    if action == "list":
        await ui.show(bot, db, chat_id, *await _list_screen(db, chat_id, lang), message_id)
        await callback.answer()
        return
    if action == "cat":
        await ui.show(bot, db, chat_id, *await _catalog_screen(db, lang), message_id)
        await callback.answer()
        return
    if action == "reg":
        await ui.show(bot, db, chat_id, *await _region_screen(db, lang, callback_data.id, callback_data.p), message_id)
        await callback.answer()
        return
    if action == "weekend":
        await callback.answer()
        await _show_weekend(bot, db, mountains, chat_id, lang, message_id)
        return
    if action == "sos":
        await callback.answer()
        await open_sos(bot, state, db, weather, chat_id, callback_data.id, message_id)
        return
    if action == "add":
        if len(await db.peaks(chat_id)) >= MAX_PEAKS:
            await callback.answer(loc("t_m_limit", n=MAX_PEAKS), show_alert=True)
            return
        await state.set_state(Form.peak_search)
        await ui.show(bot, db, chat_id, mt.add_prompt(lang), kb.mountain_add(lang), message_id)
        await callback.answer()
        return

    # Свою вершину видит только владелец: db.peak ищет её по паре (пользователь, id)
    peak = await db.resolve_peak(chat_id, callback_data.id, lang)
    if not peak:
        await ui.show(bot, db, chat_id, *await _list_screen(db, chat_id, lang), message_id)
        await callback.answer(loc["t_m_missing"], show_alert=True)
        return
    if peak.public and action in OWNER_ACTIONS:
        await callback.answer(loc["t_m_readonly"], show_alert=True)
        return

    if action in ("open", "refresh", "profile", "hourly", "outlook"):
        fresh = action == "refresh"
        text, markup = await _peak_screen(db, chat_id, action, lang, peak, mountains, admins, callback_data.p, fresh)
        await ui.show(bot, db, chat_id, text, markup, message_id)
        toast = loc["t_refreshed"] if fresh and text != texts.error(lang) else None
    elif action == "route":
        await ui.show(bot, db, chat_id, mt.route_prompt(lang, peak), kb.peak_back(lang, peak.id), message_id)
        await ui.enter_location_mode(
            bot, state, chat_id, lang, mode=Form.peak_route, hint=mt.route_hint(lang), peak_id=peak.id,
        )
    elif action == "offline":
        try:
            fc = await mountains.forecast(peak.lat, peak.lon, peak.ele)
        except WeatherError:
            await ui.show(bot, db, chat_id, texts.error(lang), kb.peak_error(lang, peak.id), message_id)
            await callback.answer()
            return
        # Отдельное сообщение, которое бот не отслеживает и не удаляет — его можно читать без сети.
        # Живое меню затем переотправляется ниже, чтобы оставаться последним в чате.
        await bot.send_message(chat_id, mt.offline(lang, peak, fc))
        await ui.send_fresh(bot, db, chat_id, mt.peak(lang, peak, fc), await _peak_keyboard(db, chat_id, lang, peak, admins))
        toast = loc["t_m_saved"]
    elif action == "edit":
        await state.set_state(Form.peak_edit)
        await state.update_data(peak_id=peak.id)
        await ui.show(bot, db, chat_id, mt.edit_prompt(lang, peak), kb.peak_back(lang, peak.id), message_id)
    elif action == "del":
        await ui.show(bot, db, chat_id, mt.delete_confirm(lang, peak), kb.peak_delete(lang, peak.id), message_id)
    elif action == "del_yes":
        await db.delete_peak(chat_id, peak.id)
        await ui.show(bot, db, chat_id, *await _list_screen(db, chat_id, lang), message_id)
        toast = loc["t_m_deleted"]
    elif action in ("pub", "pub_yes"):
        await _publish(callback, bot, db, mountains, admins, peak, lang, confirmed=action == "pub_yes")
        return
    elif action == "sub":
        await _toggle_sub(callback, bot, db, mountains, admins, peak, lang)
        return
    await callback.answer(toast)


async def _toggle_sub(
    callback: CallbackQuery, bot: Bot, db: Database, mountains: MountainService, admins: frozenset[int],
    peak: Peak, lang: str,
) -> None:
    """Подписка на прогноз выходных для вершины: по четвергам вечером и при заметных изменениях."""
    chat_id, loc = callback.from_user.id, locales.get(lang)
    subs = await db.subscriptions(chat_id)
    if peak.id in subs:
        await db.unsubscribe(chat_id, peak.id)
        toast, alert = loc["t_m_unsub"], False
    elif len(subs) >= MAX_SUBS:
        await callback.answer(loc("t_m_sub_limit", n=MAX_SUBS), show_alert=True)
        return
    else:
        await db.subscribe(chat_id, peak.id)
        toast, alert = loc["t_m_sub"], True
    text, markup = await _peak_screen(db, chat_id, "open", lang, peak, mountains, admins)
    await ui.show(bot, db, chat_id, text, markup, _message_id(callback))
    await callback.answer(toast, show_alert=alert)


async def _show_weekend(
    bot: Bot, db: Database, mountains: MountainService, chat_id: int, lang: str, message_id: int | None,
) -> None:
    """Все вершины каталога и свои — с оценкой на ближайшие выходные, лучшие сверху."""
    user = await db.get_user(chat_id)
    await ui.show(bot, db, chat_id, mt.weekend_loading(lang), None, message_id)
    days = weekend.weekend_days(timeutil.local_now(user.tz or weekend.DEFAULT_TZ).replace(tzinfo=None))
    entries = await weekend.collect(mountains, [*await db.catalog(lang), *await db.peaks(chat_id)], days)
    await ui.show(bot, db, chat_id, mt.weekend(lang, entries, days), kb.weekend(lang, entries))


@router.callback_query(GearCb.filter())
async def on_gear(
    callback: CallbackQuery, callback_data: GearCb, bot: Bot, state: FSMContext, db: Database,
    mountains: MountainService,
) -> None:
    """Что взять: чек-лист по прогнозу на выбранный день. Отметки «собрано» живут в самих кнопках."""
    chat_id, message_id = callback.from_user.id, _message_id(callback)
    lang = (await db.get_user(chat_id)).lang
    loc = locales.get(lang)
    await ui.leave_location_mode(bot, state, chat_id)
    peak = await db.resolve_peak(chat_id, callback_data.id, lang)
    if not peak:
        await ui.show(bot, db, chat_id, *await _list_screen(db, chat_id, lang), message_id)
        await callback.answer(loc["t_m_missing"], show_alert=True)
        return
    try:
        fc = await mountains.forecast(peak.lat, peak.lon, peak.ele)
    except WeatherError:
        await ui.show(bot, db, chat_id, texts.error(lang), kb.peak_error(lang, peak.id), message_id)
        await callback.answer()
        return
    days = fc.outlook()[:mt.GEAR_DAYS]
    if not days:
        await ui.show(bot, db, chat_id, texts.error(lang), kb.peak_error(lang, peak.id), message_id)
        await callback.answer()
        return
    day = min(max(callback_data.d, 0), len(days) - 1)
    checklist = gear.build(fc, days[day])
    today = fc.local_now().date()
    labels = [mt.gear_day_label(loc, o.day, today) for o in days]
    text = mt.gear(lang, peak, fc, days[day], checklist, callback_data.c)
    markup = kb.gear(lang, peak.id, labels, day, checklist.items, callback_data.c)
    await ui.show(bot, db, chat_id, text, markup, message_id)
    await callback.answer()


async def _publish(
    callback: CallbackQuery,
    bot: Bot,
    db: Database,
    mountains: MountainService,
    admins: frozenset[int],
    peak: Peak,
    lang: str,
    confirmed: bool,
) -> None:
    """Публикация своей вершины: подтверждение → заявка админам → вершина ждёт решения."""
    chat_id, message_id = callback.from_user.id, _message_id(callback)
    loc = locales.get(lang)
    if not admins:
        await callback.answer(loc["t_m_no_admin"], show_alert=True)
        return
    if peak.status == "pending":
        await callback.answer(loc["t_m_pending"], show_alert=True)
        return
    nearby = [row for row in await db.catalog_nearby(peak.lat, peak.lon) if row["source_peak_id"] != peak.id]
    if nearby:
        name = nearby[0][f"name_{lang}"] or nearby[0]["name_ru"]
        await callback.answer(loc("t_m_duplicate", name=name), show_alert=True)
        return
    if not confirmed:
        await ui.show(bot, db, chat_id, mt.publish_confirm(lang, peak), kb.publish_confirm(lang, peak.id), message_id)
        await callback.answer()
        return

    request_id = await db.submit_peak(chat_id, peak)
    if not await notify_admins(bot, db, admins, request_id, tg_author(callback.from_user)):
        await db.cancel_request(request_id)
        await callback.answer(loc["t_m_no_admin"], show_alert=True)
        return
    peak = await db.peak(chat_id, peak.id)
    text, markup = await _peak_screen(db, chat_id, "open", lang, peak, mountains, admins, header=loc["t_m_sent"])
    await ui.show(bot, db, chat_id, text, markup, message_id)
    await callback.answer(loc["t_m_sent"])


@router.message(Form.peak_search, F.text, ~F.text.startswith("/"))
async def on_peak_query(
    message: Message, bot: Bot, state: FSMContext, db: Database, weather: WeatherService, mountains: MountainService,
    admins: frozenset[int],
) -> None:
    """Координаты — как метка на карте, любой другой текст — поиск вершины по названию."""
    point = parse_coords(message.text)
    if point:
        await _add_from_point(message, bot, state, db, weather, mountains, admins, *point)
        return
    chat_id = message.chat.id
    lang = (await db.get_user(chat_id)).lang
    query = " ".join(message.text.split())[:64]
    await ui.delete_incoming(message)
    await ui.show(bot, db, chat_id, mt.searching(lang, query))
    try:
        found = await mountains.search(query, lang)
    except WeatherError:
        await ui.show(bot, db, chat_id, texts.error(lang), kb.peak_not_found(lang))
        return
    if not found:
        await ui.show(bot, db, chat_id, mt.not_found(lang, query), kb.peak_not_found(lang))
        return
    loc = locales.get(lang)
    await state.update_data(peak_results=[r.to_dict() for r in found])
    labels = [mt.result_label(loc, r) for r in found]
    await ui.show(bot, db, chat_id, mt.results(lang, query), kb.peak_results(lang, labels))


@router.message(Form.peak_search, F.location)
async def on_peak_pin(
    message: Message, bot: Bot, state: FSMContext, db: Database, weather: WeatherService, mountains: MountainService,
    admins: frozenset[int],
) -> None:
    await _add_from_point(
        message, bot, state, db, weather, mountains, admins, message.location.latitude, message.location.longitude,
    )


async def _add_from_point(
    message: Message, bot: Bot, state: FSMContext, db: Database, weather: WeatherService, mountains: MountainService,
    admins: frozenset[int], lat: float, lon: float,
) -> None:
    """Точка — метка на карте или координаты текстом. Если рядом есть вершина из OpenStreetMap —
    берём её название и высоту, иначе высоту по модели рельефа и название ближайшего места."""
    chat_id = message.chat.id
    lang = (await db.get_user(chat_id)).lang
    await ui.delete_incoming(message)
    await state.clear()
    await ui.show(bot, db, chat_id, texts.locating(lang))
    try:
        snapped = await mountains.nearest_peak(lat, lon, lang)
    except WeatherError:
        snapped = None
    if snapped:
        await _add_and_open(
            bot, db, mountains, admins, chat_id, lang, snapped.name, snapped.lat, snapped.lon, snapped.ele,
            snapped=True,
        )
        return
    try:
        ele, name = await asyncio.gather(mountains.elevations([(lat, lon)]), weather.reverse(lat, lon, lang))
    except WeatherError:
        await ui.show(bot, db, chat_id, texts.error(lang), kb.peak_not_found(lang))
        return
    await _add_and_open(
        bot, db, mountains, admins, chat_id, lang, name or mt.point_name(lang, lat, lon), lat, lon, ele[0] or 0,
        from_pin=True,
    )


@router.callback_query(PeakPickCb.filter())
async def on_peak_pick(
    callback: CallbackQuery, callback_data: PeakPickCb, bot: Bot, state: FSMContext, db: Database,
    mountains: MountainService, admins: frozenset[int],
) -> None:
    chat_id = callback.from_user.id
    lang = (await db.get_user(chat_id)).lang
    found = (await state.get_data()).get("peak_results") or []
    if callback_data.idx >= len(found):
        await callback.answer(locales.get(lang)["t_search_expired"], show_alert=True)
        return
    result = PeakResult(**found[callback_data.idx])
    await state.clear()
    ele = result.ele
    if ele is None:
        try:
            ele = (await mountains.elevations([(result.lat, result.lon)]))[0]
        except WeatherError:
            ele = None
    await _add_and_open(
        bot, db, mountains, admins, chat_id, lang, result.name, result.lat, result.lon, ele or 0,
        from_pin=result.ele is None, message_id=_message_id(callback),
    )
    await callback.answer()


@router.message(Form.peak_edit, F.text, ~F.text.startswith("/"))
async def on_peak_edit(
    message: Message, bot: Bot, state: FSMContext, db: Database, mountains: MountainService, admins: frozenset[int],
) -> None:
    """Число — новая высота, любой другой текст — новое название вершины."""
    chat_id = message.chat.id
    lang = (await db.get_user(chat_id)).lang
    loc = locales.get(lang)
    await ui.delete_incoming(message)
    peak = await db.peak(chat_id, (await state.get_data()).get("peak_id") or 0)
    if not peak:
        await state.clear()
        await ui.show(bot, db, chat_id, *await _list_screen(db, chat_id, lang))
        return

    text = message.text.strip()
    match = _ELEVATION_RE.match(text)
    if match:
        value = float(match[1].replace(",", "."))
        if not 100 <= value <= 8900:
            await ui.show(bot, db, chat_id, mt.edit_prompt(lang, peak, error=True), kb.peak_back(lang, peak.id))
            return
        peak = await db.update_peak(chat_id, peak.id, ele=round(value))
        header = loc("t_m_ele", ele=peak.ele)
    else:
        peak = await db.update_peak(chat_id, peak.id, name=text[:64])
        header = loc["t_m_renamed"]
    await state.clear()
    text, markup = await _peak_screen(db, chat_id, "open", lang, peak, mountains, admins, header=header)
    await ui.show(bot, db, chat_id, text, markup)


@router.message(Form.peak_route, F.location)
async def on_route_location(message: Message, bot: Bot, state: FSMContext, db: Database, mountains: MountainService) -> None:
    """Геопозиция на маршруте. Кнопка геопозиции остаётся под полем ввода — обновить можно одним нажатием."""
    await _route_update(message, bot, state, db, mountains, message.location.latitude, message.location.longitude)


@router.message(Form.peak_route, F.text, ~F.text.startswith("/"))
async def on_route_coords(message: Message, bot: Bot, state: FSMContext, db: Database, mountains: MountainService) -> None:
    """Координаты текстом — например, с GPS-часов или навигатора, когда кнопка геопозиции недоступна."""
    point = parse_coords(message.text)
    if point:
        await _route_update(message, bot, state, db, mountains, *point)
        return
    chat_id = message.chat.id
    await ui.delete_incoming(message)
    lang = (await db.get_user(chat_id)).lang
    peak = await db.resolve_peak(chat_id, (await state.get_data()).get("peak_id") or 0, lang)
    if peak:
        text = locales.get(lang)["coords_error"] + "\n" + mt.route_prompt(lang, peak)
        await ui.show(bot, db, chat_id, text, kb.peak_back(lang, peak.id))


async def _route_update(
    message: Message, bot: Bot, state: FSMContext, db: Database, mountains: MountainService, lat: float, lon: float,
) -> None:
    """Погода в точке на маршруте, на вершине и на высотах между ними."""
    await _delete_unless_live(message)
    await _route_refresh(bot, state, db, mountains, message.chat.id, lat, lon)


async def _route_refresh(
    bot: Bot, state: FSMContext, db: Database, mountains: MountainService, chat_id: int, lat: float, lon: float,
) -> None:
    lang = (await db.get_user(chat_id)).lang
    await _save_point(db, chat_id, lat, lon)
    peak = await db.resolve_peak(chat_id, (await state.get_data()).get("peak_id") or 0, lang)
    if not peak:
        await ui.leave_location_mode(bot, state, chat_id)
        await ui.show(bot, db, chat_id, *await _list_screen(db, chat_id, lang))
        return
    try:
        here, fc = await asyncio.gather(
            mountains.here(lat, lon, fresh=True), mountains.forecast(peak.lat, peak.lon, peak.ele, fresh=True),
        )
    except WeatherError:
        await ui.show(bot, db, chat_id, texts.error(lang), kb.peak_route(lang, peak.id))
        return
    await db.update(chat_id, route_ele=here.elevation)
    await ui.show(bot, db, chat_id, mt.route(lang, peak, fc, here), kb.peak_route(lang, peak.id))


async def _save_point(db: Database, chat_id: int, lat: float, lon: float) -> None:
    """Последняя точка с маршрута — её покажет экран SOS. Время — UTC в формате SQLite."""
    await db.update(chat_id, route_lat=lat, route_lon=lon, route_ele=None, route_at=timeutil.to_db(timeutil.utc_now()))


# ── SOS ─────────────────────────────────────────────────────────────────────

def _sos_screen(user: User, peak_id: int, place: str | None = None) -> tuple[str, InlineKeyboardMarkup]:
    lang = user.lang
    minutes = None
    if user.route_at and user.route_lat is not None and user.route_lon is not None:
        minutes = int((timeutil.utc_now() - timeutil.from_db(user.route_at)).total_seconds() // 60)
    if minutes is None or minutes > SOS_FRESH_HOURS * 60:
        return mt.sos(lang, None, None), kb.sos(lang, peak_id)
    lat, lon, ele = user.route_lat, user.route_lon, user.route_ele
    share_url = links.share(links.map_url(lat, lon), mt.sos_share_text(lang, lat, lon, ele))
    return mt.sos(lang, lat, lon, ele, minutes, place), kb.sos(lang, peak_id, share_url)


async def _sos_place(weather: WeatherService, user: User) -> str | None:
    if user.route_lat is None or user.route_lon is None:
        return None
    try:
        return await asyncio.wait_for(weather.reverse(user.route_lat, user.route_lon, user.lang), SOS_LOOKUP_SECONDS)
    except asyncio.TimeoutError:
        return None


async def open_sos(
    bot: Bot, state: FSMContext, db: Database, weather: WeatherService, chat_id: int, peak_id: int = 0,
    message_id: int | None = None, fresh: bool = False,
) -> None:
    """Экран SOS: номера экстренных служб и координаты в форматах для спасателей. Сначала показываем
    то, что есть, сразу — а ближайшее место дописываем, если сеть успеет ответить."""
    user = await db.get_user(chat_id)
    text, markup = _sos_screen(user, peak_id)
    if fresh:
        await ui.send_fresh(bot, db, chat_id, text, markup)
    else:
        await ui.show(bot, db, chat_id, text, markup, message_id)
    await ui.enter_location_mode(
        bot, state, chat_id, user.lang, mode=Form.sos, hint=mt.sos_hint(user.lang), peak_id=peak_id,
    )
    place = await _sos_place(weather, user)
    if place:
        await ui.show(bot, db, chat_id, *_sos_screen(user, peak_id, place))


@router.message(Form.sos, F.location)
async def on_sos_location(
    message: Message, bot: Bot, state: FSMContext, db: Database, weather: WeatherService, mountains: MountainService,
) -> None:
    await _sos_update(message, bot, state, db, weather, mountains, message.location.latitude, message.location.longitude)


@router.message(Form.sos, F.text, ~F.text.startswith("/"))
async def on_sos_coords(
    message: Message, bot: Bot, state: FSMContext, db: Database, weather: WeatherService, mountains: MountainService,
) -> None:
    point = parse_coords(message.text)
    if point:
        await _sos_update(message, bot, state, db, weather, mountains, *point)
        return
    chat_id = message.chat.id
    await ui.delete_incoming(message)
    user = await db.get_user(chat_id)
    text, markup = _sos_screen(user, (await state.get_data()).get("peak_id") or 0)
    await ui.show(bot, db, chat_id, locales.get(user.lang)["coords_error"] + "\n" + text, markup)


async def _sos_update(
    message: Message, bot: Bot, state: FSMContext, db: Database, weather: WeatherService, mountains: MountainService,
    lat: float, lon: float,
) -> None:
    chat_id = message.chat.id
    await _delete_unless_live(message)
    await _save_point(db, chat_id, lat, lon)
    peak_id = (await state.get_data()).get("peak_id") or 0
    user = await db.get_user(chat_id)
    await ui.show(bot, db, chat_id, *_sos_screen(user, peak_id))
    try:
        ele, place = await asyncio.wait_for(
            asyncio.gather(mountains.elevations([(lat, lon)]), weather.reverse(lat, lon, user.lang)),
            SOS_LOOKUP_SECONDS,
        )
    except (WeatherError, asyncio.TimeoutError):
        return
    user = await db.update(chat_id, route_ele=ele[0])
    await ui.show(bot, db, chat_id, *_sos_screen(user, peak_id, place))


# ── ссылки на вершины ───────────────────────────────────────────────────────

async def open_link(
    bot: Bot, db: Database, mountains: MountainService, admins: frozenset[int], chat_id: int, payload: str,
) -> bool:
    """/start p<id> — вершина каталога, s<ключ> — чужая личная вершина: её копия добавляется себе.
    False — ссылка не про вершину или вершины уже нет."""
    lang = (await db.get_user(chat_id)).lang
    loc = locales.get(lang)
    header = None
    if payload[:1] == "p" and payload[1:].isdigit():
        peak = await db.catalog_peak(int(payload[1:]), lang)
    elif payload[:1] == "s" and len(payload) > 1:
        found = await db.shared_peak(payload[1:])
        if not found:
            return False
        owner, shared = found
        own = await db.peaks(chat_id)
        peak = shared if owner == chat_id else next(
            (p for p in own if abs(p.lat - shared.lat) < SAME_PLACE and abs(p.lon - shared.lon) < SAME_PLACE), None,
        )
        if peak is None:
            if len(own) >= MAX_PEAKS:
                text, markup = await _list_screen(db, chat_id, lang)
                await ui.send_fresh(bot, db, chat_id, loc("t_m_limit", n=MAX_PEAKS) + "\n\n" + text, markup)
                return True
            peak = await db.add_peak(chat_id, shared.name, shared.lat, shared.lon, shared.ele)
            header = loc["t_m_shared_added"]
    else:
        return False
    if not peak:
        return False
    text, markup = await _peak_screen(db, chat_id, "open", lang, peak, mountains, admins, header=header)
    await ui.send_fresh(bot, db, chat_id, text, markup)
    return True



@router.edited_message(F.location, F.chat.type == ChatType.PRIVATE)
async def on_live_location(
    message: Message, bot: Bot, state: FSMContext, db: Database, mountains: MountainService,
) -> None:
    """Трансляция геопозиции: Telegram присылает новые точки правкой того же сообщения. Точку запоминаем
    для SOS и контрольного срока, а экраны обновляем не чаще LIVE_*_SECONDS — без лишних запросов к API."""
    chat_id = message.chat.id
    lat, lon = message.location.latitude, message.location.longitude
    current = await state.get_state()
    if current not in (Form.peak_route.state, Form.sos.state) and not await db.active_trip(chat_id):
        return
    data = await state.get_data()
    interval = LIVE_ROUTE_SECONDS if current == Form.peak_route.state else LIVE_SOS_SECONDS
    if current in (Form.peak_route.state, Form.sos.state) and time.time() - data.get("live_at", 0) >= interval:
        await state.update_data(live_at=time.time())
        if current == Form.peak_route.state:
            await _route_refresh(bot, state, db, mountains, chat_id, lat, lon)
        else:
            await _save_point(db, chat_id, lat, lon)
            await ui.show(bot, db, chat_id, *_sos_screen(await db.get_user(chat_id), data.get("peak_id") or 0))
        return
    # Высоту не знаем — оставим прежнюю, если точка почти не сдвинулась
    user = await db.get_user(chat_id)
    moved = user.route_lat is None or abs(user.route_lat - lat) > 0.002 or abs(user.route_lon - lon) > 0.002
    await db.update(
        chat_id, route_lat=lat, route_lon=lon, route_at=timeutil.to_db(timeutil.utc_now()),
        **({"route_ele": None} if moved else {}),
    )
