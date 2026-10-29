"""Фоновые задачи гор: прогноз на выходные по подпискам и ежедневная копия базы.

* В четверг вечером (если бот был выключен — в пятницу или утром в субботу) подписчик получает
  прогноз на выходные для своих вершин.
* Потом, до самих выходных, бот следит за прогнозом и пишет, если день, о котором уже сообщили,
  стал «не рекомендуется» или, наоборот, из плохого стал хорошим.
* Раз в сутки бот кладёт копию базы в data/backups и хранит последние BACKUP_KEEP копий.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime
from pathlib import Path

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError, TelegramRetryAfter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, StorageKey

from bot import keyboards as kb
from bot import mountain_texts as mt
from bot import timeutil, ui, weekend
from bot.db import Database, Peak, User
from bot.services import MountainService
from bot.services.mountain import DayOutlook
from bot.states import Form

log = logging.getLogger(__name__)

CHECK_SECONDS = 15 * 60
DIGEST_WEEKDAY, DIGEST_HOUR = 3, 19     # четверг, 19:00 по местному времени
QUIET_FROM, QUIET_TO = 22, 7            # ночью ничего не присылаем
SAME_DAY_UNTIL = 9                      # об изменении на сегодня сообщаем только утром
BACKUP_KEEP = 14
BUSY_STATES = {Form.peak_route.state, Form.sos.state}   # человек на маршруте — не перебиваем экран


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
