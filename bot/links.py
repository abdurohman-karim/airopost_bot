"""Ссылки: открыть вершину в боте, поделиться через Telegram, координаты на карте."""
from __future__ import annotations

from urllib.parse import quote, urlencode

from bot.db import Peak

_username: str | None = None


def init(username: str | None) -> None:
    """Имя бота для ссылок t.me — задаётся при запуске."""
    global _username
    _username = username


def peak_payload(peak: Peak) -> str | None:
    """Параметр /start: p<id> — вершина каталога, s<ключ> — чужая личная вершина, которую добавят себе."""
    if peak.public:
        return f"p{peak.catalog_id}"
    return f"s{peak.token}" if peak.token else None


def peak_link(peak: Peak) -> str | None:
    payload = peak_payload(peak)
    return f"https://t.me/{_username}?start={payload}" if _username and payload else None


def share(url: str, text: str) -> str:
    """Кнопка «Поделиться»: Telegram предложит выбрать чат и подставит ссылку с текстом."""
    return "https://t.me/share/url?" + urlencode({"url": url, "text": text}, quote_via=quote)


def map_url(lat: float, lon: float) -> str:
    return f"https://maps.google.com/?q={lat:.5f},{lon:.5f}"
