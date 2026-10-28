"""Ежедневная рассылка сводки в выбранное пользователем местное время."""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError, TelegramRetryAfter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, StorageKey

from bot import keyboards as kb
from bot import texts, timeutil, ui
from bot.db import Database, User
from bot.services import WeatherError, WeatherService

log = logging.getLogger(__name__)

TICK_SECONDS = 20
PARALLEL_SENDS = 10


async def run(bot: Bot, db: Database, weather: WeatherService, storage: BaseStorage) -> None:
    log.info("Планировщик рассылки запущен")
    while True:
        try:
            await tick(bot, db, weather, storage)
        except Exception:
            log.exception("Ошибка планировщика")
        await asyncio.sleep(TICK_SECONDS)


async def tick(bot: Bot, db: Database, weather: WeatherService, storage: BaseStorage) -> None:
    due = [user for user in await db.subscribers() if timeutil.is_due(user)]
    if not due:
        return
    semaphore = asyncio.Semaphore(PARALLEL_SENDS)

    async def worker(user: User) -> None:
        async with semaphore:
            await deliver(bot, db, weather, storage, user)

    await asyncio.gather(*(worker(user) for user in due))


async def deliver(bot: Bot, db: Database, weather: WeatherService, storage: BaseStorage, user: User) -> None:
    try:
        report = await weather.report(user.lat, user.lon)
    except WeatherError as e:
        # last_sent не обновляем — следующий тик попробует снова (в пределах CATCH_UP)
        log.warning("Сводка для %s отложена: %s", user.user_id, e)
        return

    now = timeutil.local_now(user.tz)
    text = texts.home(user, report, header=texts.greeting(now.hour))
    state = FSMContext(storage, StorageKey(bot_id=bot.id, chat_id=user.user_id, user_id=user.user_id))
    try:
        await ui.leave_location_mode(bot, state, user.user_id)
        # Сводка — новое сообщение, чтобы пришло уведомление; прежнее меню удаляется
        await ui.send_fresh(bot, db, user.user_id, text, kb.home())
    except TelegramRetryAfter as e:
        log.warning("Flood control, жду %s с", e.retry_after)
        await asyncio.sleep(e.retry_after)
        return
    except TelegramForbiddenError:
        log.info("Пользователь %s заблокировал бота — рассылка выключена", user.user_id)
        await db.update(user.user_id, notify_enabled=False)
        return
    except TelegramAPIError as e:
        log.warning("Не удалось отправить сводку %s: %s", user.user_id, e)
        return
    await db.update(user.user_id, last_sent=now.date().isoformat())
    log.info("Сводка отправлена %s", user.user_id)
