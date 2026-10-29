"""Контрольный срок: человек отмечает выход на маршрут и время возвращения. Не отметился вовремя —
бот напоминает ему, а через полчаса сообщает доверенным контактам, куда был выход, и последнюю точку."""
import logging
from datetime import timedelta

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from bot import keyboards as kb
from bot import links, locales, timeutil, ui, weekend
from bot import trip_texts as tt
from bot.db import MAX_CONTACTS, Database, Trip
from bot.handlers import mountains as mountain_screens
from bot.keyboards import TripCb
from bot.services import MountainService, WeatherError
from bot.states import Form

log = logging.getLogger(__name__)
router = Router(name="trips")


async def _invite_url(bot: Bot, db: Database, chat_id: int, lang: str) -> str | None:
    username = (await bot.me()).username
    if not username:
        return None
    link = f"https://t.me/{username}?start=c{await db.invite_token(chat_id)}"
    return links.share(link, tt.invite_share(lang))


async def trip_screen(
    bot: Bot, db: Database, mountains: MountainService, state: FSMContext, chat_id: int, peak_id: int,
    header: str | None = None, error: bool = False,
) -> tuple[str, InlineKeyboardMarkup]:
    """Идёт выход — его экран; нет — выбор срока для вершины (и ожидание времени текстом)."""
    user = await db.get_user(chat_id)
    lang = user.lang
    contacts = await db.contacts(chat_id)
    trip = await db.active_trip(chat_id)
    if trip:
        return tt.active(lang, trip, user, contacts, header), kb.trip_active(lang, trip.peak_id)
    peak = await db.resolve_peak(chat_id, peak_id, lang)
    if not peak:
        return await mountain_screens.list_screen(db, chat_id, lang)
    try:
        fc = await mountains.forecast(peak.lat, peak.lon, peak.ele)
        tz, today = fc.tz_name, fc.day(fc.local_now().date())
        sunset = today.get("sunset") if today else None
    except WeatherError:
        tz, sunset = user.tz or weekend.DEFAULT_TZ, None
    await state.set_state(Form.trip_time)
    await state.update_data(peak_id=peak.id, tz=tz)
    options = tt.deadline_options(timeutil.utc_now(), tz)
    text = tt.setup(lang, peak, contacts, sunset, error)
    return (f"{header}\n\n{text}" if header else text), kb.trip_setup(lang, peak.id, options, len(contacts))


async def _notify(bot: Bot, db: Database, trip: Trip, build) -> None:
    """Сообщение контактам — отдельным сообщением, которое бот не удалит."""
    for contact_id, _ in await db.contacts(trip.user_id):
        lang = (await db.get_user(contact_id)).lang
        try:
            await bot.send_message(contact_id, build(lang, trip))
        except TelegramAPIError as e:
            log.warning("Контакт %s не получил сообщение о выходе #%s: %s", contact_id, trip.id, e)


async def _start(
    bot: Bot, db: Database, mountains: MountainService, state: FSMContext, chat_id: int, name: str,
    peak_id: int, tz: str, deadline,
) -> tuple[str, InlineKeyboardMarkup, str]:
    lang = (await db.get_user(chat_id)).lang
    peak = await db.resolve_peak(chat_id, peak_id, lang)
    if not peak:
        text, markup = await mountain_screens.list_screen(db, chat_id, lang)
        return text, markup, locales.get(lang)["t_m_missing"]
    trip = await db.start_trip(chat_id, name, peak, tz, timeutil.to_db(timeutil.utc_now()), timeutil.to_db(deadline))
    await state.clear()
    toast = locales.get(lang)("t_trip_started", time=tt.when(locales.get(lang), trip.deadline, trip.tz))
    text, markup = await trip_screen(bot, db, mountains, state, chat_id, peak.id, header=toast)
    return text, markup, toast


@router.callback_query(TripCb.filter())
async def on_trip(
    callback: CallbackQuery, callback_data: TripCb, bot: Bot, state: FSMContext, db: Database,
    mountains: MountainService, admins: frozenset[int],
) -> None:
    chat_id, message_id = callback.from_user.id, callback.message.message_id if callback.message else None
    lang = (await db.get_user(chat_id)).lang
    loc = locales.get(lang)
    action, toast, alert = callback_data.a, None, False
    await ui.leave_location_mode(bot, state, chat_id)

    if action == "accept":
        await _accept(callback, callback_data, bot, db, lang)
        return

    trip = await db.active_trip(chat_id)
    if action == "start":
        deadline = timeutil.utc_now() + timedelta(hours=min(max(callback_data.h, 1), 24))
        peak = await db.resolve_peak(chat_id, callback_data.id, lang)
        tz = weekend.DEFAULT_TZ
        if peak:
            try:
                tz = (await mountains.forecast(peak.lat, peak.lon, peak.ele)).tz_name
            except WeatherError:
                pass
        text, markup, toast = await _start(
            bot, db, mountains, state, chat_id, callback.from_user.full_name, callback_data.id, tz, deadline,
        )
        await ui.show(bot, db, chat_id, text, markup, message_id)
    elif action in ("done", "cancel") and trip:
        await db.update_trip(trip.id, status="done" if action == "done" else "cancelled")
        if trip.alerted:
            await _notify(bot, db, trip, tt.back_notice)
        toast = loc["t_trip_done" if action == "done" else "t_trip_cancelled"]
        peak = await db.resolve_peak(chat_id, trip.peak_id, lang)
        if peak:
            text, markup = await mountain_screens.peak_screen(db, chat_id, lang, peak, mountains, admins, header=toast)
        else:
            text, markup = await mountain_screens.list_screen(db, chat_id, lang)
        await ui.show(bot, db, chat_id, text, markup, message_id)
    elif action == "extend" and trip:
        base = max(timeutil.from_db(trip.deadline), timeutil.utc_now())
        extended = await db.update_trip(
            trip.id, deadline=timeutil.to_db(base + timedelta(hours=min(max(callback_data.h, 1), 6))),
            reminded=0, alerted=0,
        )
        if trip.alerted:
            await _notify(bot, db, extended, tt.extended_notice)
        toast = loc("t_trip_extended", time=tt.when(loc, extended.deadline, extended.tz))
        text, markup = await trip_screen(bot, db, mountains, state, chat_id, trip.peak_id)
        await ui.show(bot, db, chat_id, text, markup, message_id)
    elif action == "contacts":
        people = await db.contacts(chat_id)
        markup = kb.contacts(lang, people, callback_data.id, await _invite_url(bot, db, chat_id, lang))
        await ui.show(bot, db, chat_id, tt.contacts_screen(lang, people), markup, message_id)
    elif action == "rm":
        await db.remove_contact(chat_id, callback_data.id)
        people = await db.contacts(chat_id)
        markup = kb.contacts(lang, people, callback_data.h, await _invite_url(bot, db, chat_id, lang))
        await ui.show(bot, db, chat_id, tt.contacts_screen(lang, people), markup, message_id)
        toast = loc["t_contact_removed"]
    else:
        # open, а также done/extend/cancel по кнопке, когда выхода уже нет
        await ui.show(bot, db, chat_id, *await trip_screen(bot, db, mountains, state, chat_id, callback_data.id), message_id)
    await callback.answer(toast, show_alert=alert)


@router.message(Form.trip_time, F.text, ~F.text.startswith("/"))
async def on_trip_time(message: Message, bot: Bot, state: FSMContext, db: Database, mountains: MountainService) -> None:
    """Срок текстом: «18:30» — сегодня, а если это время уже прошло — завтра."""
    chat_id = message.chat.id
    await ui.delete_incoming(message)
    data = await state.get_data()
    peak_id, tz = data.get("peak_id") or 0, data.get("tz") or weekend.DEFAULT_TZ
    value = timeutil.parse_time(message.text)
    if not value:
        await ui.show(bot, db, chat_id, *await trip_screen(bot, db, mountains, state, chat_id, peak_id, error=True))
        return
    now = tt.local(timeutil.utc_now(), tz)
    hour, minute = map(int, value.split(":"))
    deadline = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if deadline <= now:
        deadline += timedelta(days=1)
    text, markup, _ = await _start(bot, db, mountains, state, chat_id, message.from_user.full_name, peak_id, tz, deadline)
    await ui.show(bot, db, chat_id, text, markup)


# ── приглашение в доверенные контакты ───────────────────────────────────────

async def open_invite(bot: Bot, db: Database, chat_id: int, token: str) -> bool:
    """/start c<ключ>: человек открыл ссылку-приглашение. False — ключ не найден."""
    owner_id = await db.user_by_invite(token)
    if owner_id is None:
        return False
    lang = (await db.get_user(chat_id)).lang
    if owner_id == chat_id:
        await ui.send_fresh(bot, db, chat_id, locales.get(lang)["invite_own"], kb.home_only(lang))
        return True
    owner_name = (await db.get_user(owner_id)).name or str(owner_id)
    await ui.send_fresh(bot, db, chat_id, tt.invite(lang, owner_name), kb.invite(lang, owner_id, token))
    return True


async def _accept(callback: CallbackQuery, callback_data: TripCb, bot: Bot, db: Database, lang: str) -> None:
    loc = locales.get(lang)
    chat_id = callback.from_user.id
    owner_id = callback_data.id
    if await db.user_by_invite(callback_data.t) != owner_id or owner_id == chat_id:
        await callback.answer(loc["t_invite_stale"], show_alert=True)
        return
    people = await db.contacts(owner_id)
    if chat_id not in {cid for cid, _ in people} and len(people) >= MAX_CONTACTS:
        await callback.answer(loc("t_contacts_limit", n=MAX_CONTACTS), show_alert=True)
        return
    await db.add_contact(owner_id, chat_id, callback.from_user.full_name)
    owner_name = (await db.get_user(owner_id)).name or str(owner_id)
    message_id = callback.message.message_id if callback.message else None
    await ui.show(bot, db, chat_id, loc("invite_done", who=tt.escape(owner_name)), kb.home_only(lang), message_id)
    await callback.answer()

    owner_lang = (await db.get_user(owner_id)).lang
    people = await db.contacts(owner_id)
    notice = locales.get(owner_lang)("contact_added_notice", who=tt.escape(callback.from_user.full_name))
    markup = kb.contacts(owner_lang, people, 0, await _invite_url(bot, db, owner_id, owner_lang))
    try:
        await ui.send_fresh(bot, db, owner_id, f"{notice}\n\n{tt.contacts_screen(owner_lang, people)}", markup)
    except TelegramAPIError as e:
        log.info("Владелец %s не получил уведомление о новом контакте: %s", owner_id, e)
