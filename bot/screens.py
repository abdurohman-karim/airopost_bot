"""Сборка экранов: загрузка данных + текст + клавиатура."""
from __future__ import annotations

import logging

from aiogram.types import InlineKeyboardMarkup

from bot import keyboards as kb
from bot import texts
from bot.db import User
from bot.services import WeatherError, WeatherService

log = logging.getLogger(__name__)

Screen = tuple[str, InlineKeyboardMarkup]


async def build(
    screen: str,
    user: User,
    weather: WeatherService,
    *,
    page: int = 0,
    fresh: bool = False,
    name: str = "",
    header: str | None = None,
) -> Screen:
    lang = user.lang
    if screen == "settings":
        return texts.settings(user), kb.settings(user)
    if screen == "lang":
        return texts.language(lang), kb.language(lang)
    if screen == "time":
        return texts.time_hours(user), kb.time_hours(user)
    if screen == "location":
        return texts.location_prompt(lang), kb.location_prompt(user)
    if not user.has_location:
        return texts.welcome(lang, name), kb.welcome(lang)

    try:
        if screen == "hourly":
            forecast = await weather.forecast(user.lat, user.lon, fresh)
            pages = texts.hourly_pages(forecast)
            page = min(max(page, 0), pages - 1)
            return texts.hourly(user, forecast, page), kb.hourly(lang, page, pages)
        if screen == "daily":
            forecast = await weather.forecast(user.lat, user.lon, fresh)
            return texts.daily(user, forecast), kb.daily(lang)
        if screen == "air":
            air = await weather.air(user.lat, user.lon, fresh)
            return texts.air_details(user, air), kb.air(lang)
        report = await weather.report(user.lat, user.lon, fresh)
        return texts.home(user, report, header), kb.home(lang)
    except WeatherError as e:
        log.warning("Экран %s для %s: %s", screen, user.user_id, e)
        return texts.error(lang), kb.error(lang, screen)
