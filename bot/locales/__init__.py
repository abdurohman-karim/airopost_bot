"""Локализация: русский, узбекский (латиница), английский."""
from __future__ import annotations

from datetime import date
from typing import Any

from bot.locales import en, ru, uz

DEFAULT = "ru"
LANGS = ("ru", "uz", "en")
_STRINGS = {"ru": ru.STRINGS, "uz": uz.STRINGS, "en": en.STRINGS}

# Языки, носителям которых по умолчанию привычнее русский интерфейс
_RUSSIAN_SPEAKING = {"ru", "be", "uk", "kk", "ky", "tg", "tk", "az", "hy", "ka", "mo"}


def detect(language_code: str | None) -> str:
    """Язык по умолчанию из настроек Telegram пользователя."""
    if not language_code:
        return DEFAULT
    code = language_code.lower().split("-")[0]
    if code in LANGS:
        return code
    return "ru" if code in _RUSSIAN_SPEAKING else "en"


class Locale:
    def __init__(self, code: str) -> None:
        self.code = code if code in _STRINGS else DEFAULT
        self._strings = _STRINGS[self.code]

    def __getitem__(self, key: str) -> Any:
        """Сырое значение: строка, список или словарь. Нет перевода — берётся русский."""
        value = self._strings.get(key)
        return value if value is not None else ru.STRINGS[key]

    def __call__(self, key: str, **kwargs: Any) -> str:
        text = self[key]
        return text.format(**kwargs) if kwargs else text

    def num(self, value: float | None, digits: int = 0) -> str:
        if value is None:
            return "—"
        return f"{value:.{digits}f}".replace(".", self["decimal"])

    def day_month(self, d: date) -> str:
        return self("day_month", d=d.day, m=self["months"][d.month - 1])

    def date(self, d: date) -> str:
        return self("date", wd=self["weekdays"][d.weekday()], d=d.day, m=self["months"][d.month - 1])


_CACHE = {code: Locale(code) for code in LANGS}


def get(code: str | None) -> Locale:
    return _CACHE.get(code or DEFAULT, _CACHE[DEFAULT])
