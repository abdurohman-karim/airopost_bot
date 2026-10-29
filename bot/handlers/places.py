"""Избранные места: быстрое переключение местности. Поездка: на выбранные дни ежедневная сводка
переключается на место назначения, а потом возвращается домой."""
from datetime import timedelta
from html import escape

from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from bot import keyboards as kb
from bot import locales, screens, texts, timeutil, ui
from bot import place_texts as pt
from bot.db import MAX_PLACES, Database, SavedPlace, User
from bot.keyboards import PlCb
from bot.services import WeatherError, WeatherService

router = Router(name="places")

TRIP_START_DAYS = 8       # первый день поездки — не дальше чем через неделю


async def switch_home(db: Database, user: User, place: SavedPlace) -> User:
    """Сделать место домашним: погода и сводка теперь для него."""
    fields = {"lat": place.lat, "lon": place.lon, "place": place.name, "tz": place.tz or user.tz}
    if user.notify_enabled:
        fields["last_sent"] = timeutil.last_sent_after_change(fields["tz"], user.notify_time)
    return await db.update(user.user_id, **fields)


async def places_screen(db: Database, user: User, error: str | None = None) -> tuple[str, InlineKeyboardMarkup]:
    items = await db.places(user.user_id)
    dest = await db.saved_place(user.user_id, user.trip_place)
    current_saved = not user.has_location or any(db.same(p, user.lat, user.lon) for p in items)
    markup = kb.places(user.lang, items, can_save=not current_saved and len(items) < MAX_PLACES,
                       can_add=len(items) < MAX_PLACES, trip=bool(user.trip_place))
    return pt.places(user.lang, user, items, dest, error), markup


def _today(tz: str | None):
    return timeutil.local_now(tz).date()


@router.callback_query(PlCb.filter())
async def on_place(
    callback: CallbackQuery, callback_data: PlCb, bot: Bot, state: FSMContext, db: Database, weather: WeatherService,
) -> None:
    chat_id, message_id = callback.from_user.id, callback.message.message_id if callback.message else None
    user = await db.get_user(chat_id)
    lang, loc = user.lang, locales.get(user.lang)
    action, toast = callback_data.a, None
    await ui.leave_location_mode(bot, state, chat_id)

    if action == "go":
        place = await db.saved_place(chat_id, callback_data.id)
        if place:
            if user.trip_on:
                # Во время поездки дом меняется вручную — поездку считаем законченной
                await db.update(chat_id, trip_place=None, trip_from=None, trip_to=None, trip_home=None, trip_on=0)
            user = await switch_home(db, user, place)
            text, markup = await screens.build("home", user, weather, header=texts.saved_header(user))
            await ui.show(bot, db, chat_id, text, markup, message_id)
            await callback.answer(loc["t_saved"])
            return
    elif action == "del":
        await db.delete_place(chat_id, callback_data.id)
        toast = loc["t_pl_deleted"]
    elif action == "save" and user.has_location:
        saved = await db.add_place(chat_id, user.place or loc["my_place"], user.lat, user.lon, user.tz)
        toast = loc["t_pl_saved"] if saved else loc("t_pl_limit", n=MAX_PLACES)
    elif action == "add":
        if len(await db.places(chat_id)) >= MAX_PLACES:
            await callback.answer(loc("t_pl_limit", n=MAX_PLACES), show_alert=True)
            return
        await ui.show(bot, db, chat_id, loc["pl_add_prompt"] + "\n\n" + texts.location_prompt(lang),
                      kb.places_back(lang), message_id)
        await ui.enter_location_mode(bot, state, chat_id, lang, fav=1)
        await callback.answer()
        return
    elif action == "trip":
        items = [p for p in await db.places(chat_id) if not (user.has_location and db.same(p, user.lat, user.lon))]
        await ui.show(bot, db, chat_id, pt.trip_dest(lang, bool(items)), kb.trip_dest(lang, items), message_id)
        await callback.answer()
        return
    elif action in ("tdest", "tlen", "tset"):
        dest = await db.saved_place(chat_id, callback_data.id)
        if dest:
            today = _today(dest.tz)
            if action == "tdest":
                days = [today + timedelta(days=i) for i in range(TRIP_START_DAYS)]
                labels = [loc["today"], loc["tomorrow"], *(f"{loc['weekdays'][d.weekday()]} {d.day}" for d in days[2:])]
                await ui.show(bot, db, chat_id, pt.trip_from(lang, dest), kb.trip_from(lang, dest.id, labels), message_id)
            elif action == "tlen":
                offset = min(max(callback_data.d, 0), TRIP_START_DAYS - 1)
                start = today + timedelta(days=offset)
                await ui.show(bot, db, chat_id, pt.trip_len(lang, dest, start), kb.trip_len(lang, dest.id, offset),
                              message_id)
            else:
                offset, days = divmod(callback_data.d, 100)
                start = today + timedelta(days=min(max(offset, 0), TRIP_START_DAYS - 1))
                end = start + timedelta(days=min(max(days, 1), 30) - 1)
                user = await db.update(chat_id, trip_place=dest.id, trip_from=start.isoformat(), trip_to=end.isoformat(),
                                       trip_on=0)
                await ui.show(bot, db, chat_id, *await places_screen(db, user), message_id)
                await callback.answer(loc["t_pl_trip_set"], show_alert=True)
            if action != "tset":
                await callback.answer()
            return
    elif action == "tcancel":
        if user.trip_on:
            home = await db.saved_place(chat_id, user.trip_home)
            if home:
                user = await switch_home(db, user, home)
        user = await db.update(chat_id, trip_place=None, trip_from=None, trip_to=None, trip_home=None, trip_on=0)
        toast = loc["t_pl_trip_cancelled"]

    user = await db.get_user(chat_id)
    await ui.show(bot, db, chat_id, *await places_screen(db, user), message_id)
    await callback.answer(toast)


async def add_favorite(
    bot: Bot, db: Database, weather: WeatherService, chat_id: int, lat: float, lon: float, title: str,
    message_id: int | None = None,
) -> None:
    """Новое место из поиска или геолокации — в избранное, домашняя местность не меняется."""
    user = await db.get_user(chat_id)
    try:
        tz = (await weather.forecast(lat, lon)).tz_name
    except WeatherError:
        tz = None
    saved = await db.add_place(chat_id, title, lat, lon, tz)
    error = None if saved else "t_pl_limit_plain"
    text, markup = await places_screen(db, user, error)
    if saved:
        text = locales.get(user.lang)("t_pl_added", name=escape(saved.name)) + "\n\n" + text
    await ui.show(bot, db, chat_id, text, markup, message_id)

