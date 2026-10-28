from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from bot import locales
from bot.db import User
from bot.locales import LANGS
from bot.services import Place


class Nav(CallbackData, prefix="nav"):
    to: str             # home | hourly | daily | air | settings | location | time | toggle | lang
    page: int = 0
    fresh: bool = False


class PlaceCb(CallbackData, prefix="place"):
    idx: int


class TimeCb(CallbackData, prefix="time"):
    hour: int
    minute: int = -1    # -1 — час выбран, теперь показать минуты


class LangCb(CallbackData, prefix="lang"):
    code: str
    back: str = "settings"   # экран, который показать после выбора


def _btn(text: str, data: CallbackData) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=data.pack())


def _back(lang: str, to: str = "home", key: str = "btn_back") -> list[InlineKeyboardButton]:
    return [_btn(locales.get(lang)[key], Nav(to=to))]


def _lang_row(back: str) -> list[InlineKeyboardButton]:
    return [_btn(locales.get(code)["lang_name"], LangCb(code=code, back=back)) for code in LANGS]


def welcome(lang: str) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_pick_place"], Nav(to="location"))],
        _lang_row("home"),
    ])


def home(lang: str) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_refresh"], Nav(to="home", fresh=True))],
        [_btn(loc["btn_hourly"], Nav(to="hourly")), _btn(loc["btn_daily"], Nav(to="daily"))],
        [_btn(loc["btn_air"], Nav(to="air"))],
        [_btn(loc["btn_settings"], Nav(to="settings"))],
    ])


def hourly(lang: str, page: int, pages: int) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    row = []
    if page > 0:
        row.append(_btn(loc["btn_earlier"], Nav(to="hourly", page=page - 1)))
    if page < pages - 1:
        row.append(_btn(loc["btn_later"], Nav(to="hourly", page=page + 1)))
    rows = [row] if row else []
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _back(lang)])


def daily(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(locales.get(lang)["btn_hourly"], Nav(to="hourly"))],
        _back(lang),
    ])


def air(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(locales.get(lang)["btn_refresh"], Nav(to="air", fresh=True))],
        _back(lang),
    ])


def settings(user: User) -> InlineKeyboardMarkup:
    loc = locales.get(user.lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_change_place"] if user.has_location else loc["btn_pick_place"], Nav(to="location"))],
        [_btn(loc("btn_time", time=user.notify_time), Nav(to="time"))],
        [_btn(loc["btn_notify_off"] if user.notify_enabled else loc["btn_notify_on"], Nav(to="toggle"))],
        [_btn(loc["btn_lang"], Nav(to="lang"))],
        _back(user.lang),
    ])


def language(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        *([_btn(locales.get(code)["lang_name"] + (" ✓" if code == lang else ""), LangCb(code=code))]
          for code in LANGS),
        _back(lang, "settings"),
    ])


def _place_back(user: User) -> str:
    return "settings" if user.has_location else "home"


def location_prompt(user: User) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[_back(user.lang, _place_back(user))])


def location_reply(lang: str) -> ReplyKeyboardMarkup:
    loc = locales.get(lang)
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=loc["btn_send_location"], request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=loc["placeholder"],
    )


def search_results(places: list[Place], user: User) -> InlineKeyboardMarkup:
    rows = [[_btn(f"📍 {p.full}", PlaceCb(idx=i))] for i, p in enumerate(places)]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _back(user.lang, _place_back(user), "btn_cancel")])


def not_found(user: User) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(locales.get(user.lang)["btn_search_again"], Nav(to="location"))],
        _back(user.lang, _place_back(user)),
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
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _back(user.lang, "settings")])


def time_minutes(lang: str, hour: int) -> InlineKeyboardMarkup:
    rows = [
        [_btn(f"{hour:02d}:{m:02d}", TimeCb(hour=hour, minute=m)) for m in range(start, start + 20, 5)]
        for start in range(0, 60, 20)
    ]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _back(lang, "time")])


def error(lang: str, screen: str) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_retry"], Nav(to=screen, fresh=True))],
        [_btn(loc["btn_settings"], Nav(to="settings"))],
    ])
