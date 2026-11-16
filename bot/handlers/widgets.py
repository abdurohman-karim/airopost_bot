"""Запросы из виджета прогноза: кнопка «Обновить» внутри сообщения."""
import asyncio
import logging

from aiogram import Bot, Router
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.types import WidgetQuery

from bot import widgets
from bot.db import Database
from bot.services import MountainService, WeatherError

router = Router(name="widgets")
log = logging.getLogger(__name__)

# Telegram ждёт ответ на запрос 15 секунд — прогноз ждём меньше, чтобы успеть ответить
REFRESH_SECONDS = 11


@router.widget_query()
async def on_widget_query(query: WidgetQuery, bot: Bot, db: Database, mountains: MountainService) -> None:
    peak_id = widgets.refresh_peak_id(query.data)
    if peak_id is None or not query.chat or not query.message_id:
        await query.answer(data="err")
        return
    user = await db.get_user(query.from_user.id)
    # Своя вершина находится только у владельца — чужой id из запроса ничего не даст
    peak = await db.resolve_peak(query.from_user.id, peak_id, user.lang)
    if not peak:
        await query.answer(data="err")
        return
    try:
        fc = await asyncio.wait_for(mountains.forecast(peak.lat, peak.lon, peak.ele, fresh=True), REFRESH_SECONDS)
        await bot.edit_message_widget_data(
            chat_id=query.chat.id, message_id=query.message_id,
            chat_data=widgets.forecast_data(peak.id, fc, user.lang),
        )
    except (WeatherError, asyncio.TimeoutError):
        await query.answer(data="err")
        return
    except TelegramBadRequest as e:
        if "not modified" not in e.message:
            log.warning("Не удалось обновить виджет %s/%s: %s", query.chat.id, query.message_id, e.message)
            await query.answer(data="err")
            return
    try:
        await query.answer(data="ok")
    except TelegramAPIError:
        pass
