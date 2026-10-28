from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import keyboards as kb
from bot import locales, screens, texts, timeutil, ui
from bot.db import Database
from bot.keyboards import PlaceCb
from bot.services import Place, WeatherError, WeatherService
from bot.states import Form

router = Router(name="location")


async def save_location(
    bot: Bot,
    db: Database,
    weather: WeatherService,
    chat_id: int,
    lat: float,
    lon: float,
    title: str,
    name: str,
    message_id: int | None = None,
) -> None:
    user = await db.get_user(chat_id)
    try:
        # Прогноз нужен ещё и ради часового пояса — по нему считается время рассылки
        forecast = await weather.forecast(lat, lon)
    except WeatherError:
        await ui.show(bot, db, chat_id, texts.error(user.lang), kb.not_found(user), message_id)
        return

    fields = {"lat": lat, "lon": lon, "place": title, "tz": forecast.tz_name}
    if user.notify_enabled:
        fields["last_sent"] = timeutil.last_sent_after_change(forecast.tz_name, user.notify_time)
    user = await db.update(chat_id, **fields)
    text, markup = await screens.build("home", user, weather, name=name, header=texts.saved_header(user))
    await ui.show(bot, db, chat_id, text, markup, message_id)


@router.message(F.location)
async def on_location(message: Message, bot: Bot, state: FSMContext, db: Database, weather: WeatherService) -> None:
    """Геолокация принимается в любой момент — и кнопкой, и через «скрепку»."""
    chat_id = message.chat.id
    lat, lon = message.location.latitude, message.location.longitude
    await ui.delete_incoming(message)
    await ui.leave_location_mode(bot, state, chat_id)
    user = await db.get_user(chat_id)
    await ui.show(bot, db, chat_id, texts.locating(user.lang))
    title = await weather.reverse(lat, lon, user.lang) or f"{lat:.3f}, {lon:.3f}"
    await save_location(bot, db, weather, chat_id, lat, lon, title, message.from_user.first_name)


@router.message(StateFilter(None, Form.location), F.text, ~F.text.startswith("/"))
async def on_search(message: Message, bot: Bot, state: FSMContext, db: Database, weather: WeatherService) -> None:
    """Любой текст вне других режимов — поиск местности по названию."""
    chat_id = message.chat.id
    query = " ".join(message.text.split())[:64]
    await ui.delete_incoming(message)
    await ui.leave_location_mode(bot, state, chat_id)
    user = await db.get_user(chat_id)
    await ui.show(bot, db, chat_id, texts.searching(user.lang, query))

    try:
        places = await weather.search(query, user.lang)
    except WeatherError:
        await ui.show(bot, db, chat_id, texts.error(user.lang), kb.not_found(user))
        return
    if not places:
        await ui.show(bot, db, chat_id, texts.not_found(user.lang, query), kb.not_found(user))
        return
    if len(places) == 1:
        place = places[0]
        await save_location(bot, db, weather, chat_id, place.lat, place.lon, place.short, message.from_user.first_name)
        return

    await state.update_data(places=[p.to_dict() for p in places])
    await ui.show(bot, db, chat_id, texts.search_results(user.lang, query), kb.search_results(places, user))


@router.callback_query(PlaceCb.filter())
async def on_place(
    callback: CallbackQuery,
    callback_data: PlaceCb,
    bot: Bot,
    state: FSMContext,
    db: Database,
    weather: WeatherService,
) -> None:
    chat_id = callback.from_user.id
    loc = locales.get((await db.get_user(chat_id)).lang)
    places = (await state.get_data()).get("places") or []
    if callback_data.idx >= len(places):
        await callback.answer(loc["t_search_expired"], show_alert=True)
        return
    place = Place(**places[callback_data.idx])
    await ui.leave_location_mode(bot, state, chat_id)
    await save_location(
        bot, db, weather, chat_id, place.lat, place.lon, place.short, callback.from_user.first_name,
        message_id=callback.message.message_id if callback.message else None,
    )
    await callback.answer(loc["t_saved"])
