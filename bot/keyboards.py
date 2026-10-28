from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from bot.db import User
from bot.services import Place


class Nav(CallbackData, prefix="nav"):
    to: str             # home | hourly | daily | air | settings | location | time | toggle
    page: int = 0
    fresh: bool = False


class PlaceCb(CallbackData, prefix="place"):
    idx: int


class TimeCb(CallbackData, prefix="time"):
    hour: int
    minute: int = -1    # -1 — час выбран, теперь показать минуты


def _btn(text: str, data: CallbackData) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=data.pack())


def _back(to: str = "home", text: str = "⬅️ Назад") -> list[InlineKeyboardButton]:
    return [_btn(text, Nav(to=to))]


def welcome() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[_btn("📍 Выбрать местность", Nav(to="location"))]])


def home() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("🔄 Обновить", Nav(to="home", fresh=True))],
        [_btn("🕐 По часам", Nav(to="hourly")), _btn("📅 На 7 дней", Nav(to="daily"))],
        [_btn("🌫 Качество воздуха", Nav(to="air"))],
        [_btn("⚙️ Настройки", Nav(to="settings"))],
    ])


def hourly(page: int, pages: int) -> InlineKeyboardMarkup:
    row = []
    if page > 0:
        row.append(_btn("◀️ Раньше", Nav(to="hourly", page=page - 1)))
    if page < pages - 1:
        row.append(_btn("Позже ▶️", Nav(to="hourly", page=page + 1)))
    rows = [row] if row else []
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _back()])


def daily() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("🕐 По часам", Nav(to="hourly"))],
        _back(),
    ])


def air() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("🔄 Обновить", Nav(to="air", fresh=True))],
        _back(),
    ])


def settings(user: User) -> InlineKeyboardMarkup:
    toggle = "🔕 Выключить сводку" if user.notify_enabled else "🔔 Включить сводку"
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("📍 Изменить местность" if user.has_location else "📍 Выбрать местность", Nav(to="location"))],
        [_btn(f"⏰ Время сводки: {user.notify_time}", Nav(to="time"))],
        [_btn(toggle, Nav(to="toggle"))],
        _back(),
    ])


def location_prompt(user: User) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[_back("settings" if user.has_location else "home")])


def location_reply() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Название города…",
    )


def search_results(places: list[Place], user: User) -> InlineKeyboardMarkup:
    rows = [[_btn(f"📍 {p.full}", PlaceCb(idx=i))] for i, p in enumerate(places)]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _back("settings" if user.has_location else "home", "⬅️ Отмена")])


def not_found(user: User) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("📍 Искать снова", Nav(to="location"))],
        _back("settings" if user.has_location else "home"),
    ])


def time_hours(user: User) -> InlineKeyboardMarkup:
    current = int(user.notify_time[:2])
    rows = [
        [
            _btn(f"• {h:02d} •" if h == current else f"{h:02d}", TimeCb(hour=h))
            for h in range(start, start + 6)
        ]
        for start in range(0, 24, 6)
    ]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _back("settings")])


def time_minutes(hour: int) -> InlineKeyboardMarkup:
    rows = [
        [_btn(f"{hour:02d}:{m:02d}", TimeCb(hour=hour, minute=m)) for m in range(start, start + 20, 5)]
        for start in range(0, 60, 20)
    ]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _back("time")])


def error(screen: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("🔄 Повторить", Nav(to=screen, fresh=True))],
        [_btn("⚙️ Настройки", Nav(to="settings"))],
    ])
