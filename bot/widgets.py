"""HTML-виджет прогноза на вершине (Bot API 10.4): дни и часы в одном сообщении.

Код виджета один на язык и после отправки не меняется. Прогноз лежит в данных сообщения
(chat_data, до 1 КБ) — кнопка «Обновить» внутри виджета просит бота подтянуть свежий прогноз,
и бот меняет только данные, без новой отправки. Виджет работает без сети: всё, что он
показывает, бот кладёт в данные сам.
"""
from __future__ import annotations

import json
import re
import time
import zlib
from functools import lru_cache
from html import escape
from pathlib import Path

from bot import locales
from bot.db import Peak
from bot.mountain_texts import RATING_ICON, _hours_span, _reasons, peak_header
from bot.services.mountain import BAD_WIND, CAUTION_WIND, DAY_HOURS, MountainForecast
from bot.texts import hm, weather

TEMPLATE = Path(__file__).with_name("forecast_widget.html")
DATA_LIMIT = 1024         # байт: chat_data
HTML_LIMIT = 4096         # байт после zlib -9 — так проверяет сервер Telegram
MAX_DAYS = 7
REFRESH_PREFIX = "r"      # запрос виджета «r<id вершины>»
# Telegram может не пускать бота к виджетам (с 13.11.2026 обычным ботам отвечает
# INPUT_MEDIA_WIDGET_NOT_ALLOWED). Тогда кнопку прячем и пробуем снова через это время.
RETRY_SECONDS = 6 * 3600

# Одно число — один символ: '#'..'}' без '\' (кавычки и обратная косая в JSON экранируются)
_ALPHABET = "".join(chr(c) for c in range(35, 126) if c != 92)
_MISSING = "~"
_SHIFT = 60               # температура и ощущаемая: −60…+29 °C
_TAGS = re.compile(r"<[^>]+>")


_blocked_until = 0.0


def available() -> bool:
    return time.monotonic() >= _blocked_until


def mark_blocked() -> None:
    global _blocked_until
    _blocked_until = time.monotonic() + RETRY_SECONDS


def _enc(value: float | None, shift: int = 0) -> str:
    if value is None:
        return _MISSING
    return _ALPHABET[min(max(round(value) + shift, 0), len(_ALPHABET) - 1)]


def _hours(fc: MountainForecast, day, loc, icons: list[str]) -> str:
    """13 светлых часов дня, по 5 символов: температура, ощущаемая, ветер, вероятность осадков ×10, значок."""
    rows = {h["time"].hour: h for h in fc.hourly if h["time"].date() == day and h["time"].hour in DAY_HOURS}
    out = []
    for hour in DAY_HOURS:
        h = rows.get(hour)
        if h is None:
            out.append(_MISSING * 5)
            continue
        c = fc.summit(h)
        icon, _ = weather(loc, c.weather_code, c.is_day)
        if icon not in icons:
            icons.append(icon)
        prob = None if c.precip_prob is None else c.precip_prob / 10
        out.append(_enc(c.temp, _SHIFT) + _enc(c.feels, _SHIFT) + _enc(c.wind) + _enc(prob) + _enc(icons.index(icon)))
    return "".join(out)


def forecast_data(peak_id: int, fc: MountainForecast, lang: str) -> str:
    """Данные виджета. Не влезают в 1 КБ — сначала короче причины, потом меньше дней."""
    loc = locales.get(lang)
    now = fc.local_now()
    outlook = fc.outlook()[:MAX_DAYS]
    icons: list[str] = []
    days = [
        [o.day.day, o.day.weekday(), min((o.day - now.date()).days, 2), o.rating[0],
         _hours_span(*o.best) if o.best else "", o, _hours(fc, o.day, loc, icons)]
        for o in outlook
    ]

    def dump(days: list, full: bool) -> str:
        packed = [
            [*d[:5], _TAGS.sub("", _reasons(loc, d[5].reasons if full else d[5].reasons[:1])), d[6]]
            for d in days
        ]
        return json.dumps({
            "k": peak_id,
            "u": hm(now),
            "n": now.hour if outlook and outlook[0].day == now.date() else -1,
            "i": icons,
            "d": packed,
        }, ensure_ascii=False, separators=(",", ":"))

    for count in range(len(days), 0, -1):
        for full in (True, False):
            data = dump(days[:count], full)
            if len(data.encode()) <= DATA_LIMIT:
                return data
    return dump([], False)


@lru_cache(maxsize=None)
def forecast_html(lang: str) -> str:
    loc = locales.get(lang)
    labels = {
        "wd": loc["weekdays"],
        "today": loc["today"],
        "tomorrow": loc["tomorrow"],
        "g": loc["m_good"], "c": loc["m_caution"], "b": loc["m_bad"],
        "icons": {"g": RATING_ICON["good"], "c": RATING_ICON["caution"], "b": RATING_ICON["bad"]},
        "best": _TAGS.sub("", loc["m_best"]),
        "air": loc["w_air"],
        "feels": loc["w_feels"],
        "ms": loc["ms"],
        "upd": loc["w_updated"],
        "refresh": loc["w_refresh"],
        "err": loc["w_error"],
        "wait": loc["w_wait"],
        "none": loc["w_none"],
    }
    source = TEMPLATE.read_text(encoding="utf-8")
    source = source.replace("__L__", json.dumps(labels, ensure_ascii=False))
    source = source.replace("__W__", json.dumps([CAUTION_WIND, BAD_WIND]))
    # Отступы и пустые строки не нужны ни HTML, ни CSS, ни JS — сервер считает байты
    return "\n".join(line.strip() for line in source.splitlines() if line.strip())


def html_size(html: str) -> int:
    return len(zlib.compress(html.encode(), 9))


def caption(lang: str, peak: Peak) -> str:
    loc = locales.get(lang)
    return f"{peak_header(loc, peak)}\n<i>{escape(loc['w_hint'])}</i>"


def refresh_peak_id(data: str) -> int | None:
    if not data.startswith(REFRESH_PREFIX):
        return None
    try:
        return int(data[len(REFRESH_PREFIX):])
    except ValueError:
        return None
