"""Фоновые задачи гор: прогноз на выходные по подпискам и ежедневная копия базы.

* В четверг вечером (если бот был выключен — в пятницу или утром в субботу) подписчик получает
  прогноз на выходные для своих вершин.
* Потом, до самих выходных, бот следит за прогнозом и пишет, если день, о котором уже сообщили,
  стал «не рекомендуется» или, наоборот, из плохого стал хорошим.
* Раз в сутки бот кладёт копию базы в data/backups и хранит последние BACKUP_KEEP копий.
* Каждую минуту — контрольные сроки: прошёл срок — напоминание самому, ещё через TRIP_GRACE —
  тревога доверенным контактам с маршрутом и последней точкой.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, timedelta
from pathlib import Path

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError, TelegramRetryAfter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, StorageKey

from bot import keyboards as kb
from bot import mountain_texts as mt
from bot import spot_texts as st
from bot import timeutil, ui, weekend
from bot import trip_texts as tt
from bot.catalog import RESORTS
from bot.db import Database, Peak, User
from bot.services import MountainService, WeatherError
from bot.services.mountain import DayOutlook
from bot.states import Form

log = logging.getLogger(__name__)

CHECK_SECONDS = 15 * 60
DIGEST_WEEKDAY, DIGEST_HOUR = 3, 19     # четверг, 19:00 по местному времени
QUIET_FROM, QUIET_TO = 22, 7            # ночью ничего не присылаем
SAME_DAY_UNTIL = 9                      # об изменении на сегодня сообщаем только утром
BACKUP_KEEP = 14
BUSY_STATES = {Form.peak_route.state, Form.sos.state}   # человек на маршруте — не перебиваем экран
TRIP_SECONDS = 60
TRIP_GRACE = timedelta(minutes=30)      # столько ждём ответа на напоминание, прежде чем поднять тревогу


async def run_trips(bot: Bot, db: Database) -> None:
    log.info("Контроль сроков возвращения запущен")
    while True:
        try:
            await watch_trips(bot, db)
        except Exception:
            log.exception("Ошибка контроля сроков")
        await asyncio.sleep(TRIP_SECONDS)


async def watch_trips(bot: Bot, db: Database) -> None:
    now = timeutil.utc_now()
    for trip in await db.overdue_trips(timeutil.to_db(now)):
        owner = await db.get_user(trip.user_id)
        if not trip.reminded:
            # Напоминание — новым сообщением, чтобы пришло уведомление. Кнопку геопозиции не трогаем.
            try:
                await ui.send_fresh(bot, db, trip.user_id, tt.reminder(owner.lang, trip),
                                    kb.trip_reminder(owner.lang, trip.peak_id))
            except TelegramAPIError as e:
                log.warning("Напоминание о сроке #%s не доставлено: %s", trip.id, e)
            await db.update_trip(trip.id, reminded=1)
            continue
        if now < timeutil.from_db(trip.deadline) + TRIP_GRACE:
            continue
        contacts = await db.contacts(trip.user_id)
        for contact_id, _ in contacts:
            lang = (await db.get_user(contact_id)).lang
            try:
                # Отдельное сообщение, которое бот не удалит и не заменит
                await bot.send_message(contact_id, tt.alarm(lang, trip, owner))
            except TelegramAPIError as e:
                log.warning("Тревога по выходу #%s не доставлена контакту %s: %s", trip.id, contact_id, e)
        await db.update_trip(trip.id, alerted=1)
        log.warning("Контрольный срок #%s пропущен — сообщено контактам: %s", trip.id, len(contacts))
        if contacts:
            try:
                await ui.send_fresh(bot, db, trip.user_id, tt.owner_alerted(owner.lang, trip, contacts),
                                    kb.trip_reminder(owner.lang, trip.peak_id))
            except TelegramAPIError:
                pass


async def run(bot: Bot, db: Database, mountains: MountainService, storage: BaseStorage, backups: Path) -> None:
    log.info("Прогноз на выходные и резервные копии запущены")
    while True:
        try:
            await backup(db, backups)
        except Exception:
            log.exception("Не удалось сделать резервную копию базы")
        try:
            await tick(bot, db, mountains, storage)
        except Exception:
            log.exception("Ошибка рассылки прогноза на выходные")
        try:
            await powder(bot, db, mountains, storage)
        except Exception:
            log.exception("Ошибка оповещений о свежем снеге")
        await asyncio.sleep(CHECK_SECONDS)


async def backup(db: Database, folder: Path) -> None:
    target = folder / f"bot-{date.today().isoformat()}.db"
    if target.exists():
        return
    await db.backup(target)
    for old in sorted(folder.glob("bot-*.db"))[:-BACKUP_KEEP]:
        old.unlink(missing_ok=True)
    log.info("Резервная копия базы: %s", target)


def _digest_due(user: User, now: datetime, key: str) -> bool:
    if user.digest_week == key:
        return False
    wd = now.weekday()
    return (wd == DIGEST_WEEKDAY and now.hour >= DIGEST_HOUR) or wd == DIGEST_WEEKDAY + 1 or (wd == 5 and now.hour < 12)


async def tick(bot: Bot, db: Database, mountains: MountainService, storage: BaseStorage) -> None:
    for user_id, subs in (await db.all_subscriptions()).items():
        user = await db.get_user(user_id)
        now = timeutil.local_now(user.tz or weekend.DEFAULT_TZ).replace(tzinfo=None)
        if now.hour >= QUIET_FROM or now.hour < QUIET_TO:
            continue
        state = FSMContext(storage, StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id))
        if await state.get_state() in BUSY_STATES:
            continue
        days = weekend.weekend_days(now)
        key = weekend.weekend_key(days)
        try:
            if _digest_due(user, now, key):
                await _send_digest(bot, db, mountains, state, user, subs, days, key)
            elif user.digest_week == key:
                await _send_changes(bot, db, mountains, state, user, subs, now)
        except TelegramForbiddenError:
            log.info("Пользователь %s заблокировал бота — подписки на вершины сняты", user_id)
            for peak_id in subs:
                await db.unsubscribe(user_id, peak_id)
        except TelegramRetryAfter as e:
            log.warning("Flood control, жду %s с", e.retry_after)
            await asyncio.sleep(e.retry_after)
        except TelegramAPIError as e:
            log.warning("Прогноз на выходные для %s не отправлен: %s", user_id, e)


async def _peaks(db: Database, user: User, subs: dict[int, dict]) -> list[Peak]:
    """Вершины подписок; исчезнувшие (удалённые, снятые с каталога) — отписываем."""
    peaks = []
    for peak_id in subs:
        peak = await db.resolve_peak(user.user_id, peak_id, user.lang)
        if peak:
            peaks.append(peak)
        else:
            await db.unsubscribe(user.user_id, peak_id)
    return peaks


def _snapshot(outlooks: list[DayOutlook]) -> dict[str, str]:
    return {o.day.isoformat(): o.rating for o in outlooks}


async def _send_digest(
    bot: Bot, db: Database, mountains: MountainService, state: FSMContext, user: User,
    subs: dict[int, dict], days: list[date], key: str,
) -> None:
    entries = await weekend.collect(mountains, await _peaks(db, user, subs), days)
    if not entries:
        return     # прогноз недоступен — попробуем в следующий раз
    await ui.leave_location_mode(bot, state, user.user_id)
    await ui.send_fresh(bot, db, user.user_id, mt.digest(user.lang, entries, days), kb.digest(user.lang, entries))
    await db.update(user.user_id, digest_week=key)
    for entry in entries:
        await db.set_snapshot(user.user_id, entry.peak.id, _snapshot(entry.days))
    log.info("Прогноз на выходные отправлен %s", user.user_id)


def _changed(told: str | None, now: str) -> bool:
    return (told in ("good", "caution") and now == "bad") or (told == "bad" and now == "good")


async def _send_changes(
    bot: Bot, db: Database, mountains: MountainService, state: FSMContext, user: User,
    subs: dict[int, dict], now: datetime,
) -> None:
    today = now.date()
    # Дни, о которых уже сообщили и которые ещё впереди (сегодняшний — только утром)
    watched = {
        peak_id: {d for d in snapshot if date.fromisoformat(d) > today
                  or (date.fromisoformat(d) == today and now.hour < SAME_DAY_UNTIL)}
        for peak_id, snapshot in subs.items()
    }
    peaks = [p for p in await _peaks(db, user, subs) if watched.get(p.id)]
    if not peaks:
        return
    days = sorted({date.fromisoformat(d) for p in peaks for d in watched[p.id]})
    changed: list[tuple[Peak, DayOutlook]] = []
    snapshots: dict[int, dict] = {}
    for entry in await weekend.collect(mountains, peaks, days):
        told = subs[entry.peak.id]
        updates = [o for o in entry.days
                   if o.day.isoformat() in watched[entry.peak.id] and _changed(told.get(o.day.isoformat()), o.rating)]
        if updates:
            changed += [(entry.peak, o) for o in updates]
            snapshots[entry.peak.id] = {**told, **_snapshot(updates)}
    if not changed:
        return
    await ui.leave_location_mode(bot, state, user.user_id)
    peaks_changed = list({p.id: p for p, _ in changed}.values())
    await ui.send_fresh(bot, db, user.user_id, mt.changes(user.lang, changed, today), kb.changes(user.lang, peaks_changed))
    # Снимок меняем только после отправки — иначе при ошибке пользователь так и не узнает об изменении
    for peak_id, snapshot in snapshots.items():
        await db.set_snapshot(user.user_id, peak_id, snapshot)
    log.info("Изменение прогноза на выходные отправлено %s", user.user_id)


POWDER_HOURS = range(7, 11)   # о свежем снеге сообщаем утром, пока ещё можно успеть на склон


async def powder(bot: Bot, db: Database, mountains: MountainService, storage: BaseStorage) -> None:
    """Утром, если наверху курорта за сутки выпало не меньше POWDER_CM снега, — оповещение подписчикам."""
    subs = await db.all_ski_subs()
    if not subs:
        return
    resorts = {r[0]: r for r in RESORTS}
    for row in subs:
        raw = resorts.get(row["resort"])
        if not raw:
            continue
        user = await db.get_user(row["user_id"])
        resort = st.resorts(user.lang, [raw])[0]
        try:
            fc = await mountains.forecast(resort.lat, resort.lon, resort.top)
        except WeatherError:
            continue
        now = fc.local_now()
        if now.hour not in POWDER_HOURS or row["last_alert"] == now.date().isoformat():
            continue
        state = FSMContext(storage, StorageKey(bot_id=bot.id, chat_id=user.user_id, user_id=user.user_id))
        if await state.get_state() in BUSY_STATES:
            continue
        snow = st.ski_now(resort, fc)
        if not snow.powder:
            continue
        try:
            await ui.send_fresh(bot, db, user.user_id, st.powder_alert(user.lang, resort, snow),
                                kb.resort(user.lang, resort.key, True))
        except TelegramForbiddenError:
            await db.toggle_ski_sub(user.user_id, resort.key)
            continue
        except TelegramAPIError as e:
            log.warning("Оповещение о снеге для %s не отправлено: %s", user.user_id, e)
            continue
        await db.ski_alerted(user.user_id, resort.key, now.date().isoformat())
