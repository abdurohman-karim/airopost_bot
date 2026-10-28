"""Координаты, введённые текстом, — как альтернатива отправке геопозиции.

Понимает форматы, которые выдают карты и навигаторы:
    41.49519, 70.058671          41,49519 70,058671          -33.8568 151.2153
    41.49519°N 70.058671°E       N41.49519 E70.058671         41.49519 С, 70.058671 В
    41°29'42.7"N 70°03'31.2"E    (градусы, минуты, секунды — так копирует Google Maps)
    https://maps.google.com/?q=41.49519,70.058671   …/@41.49519,70.058671,15z   geo:41.49519,70.058671
"""
from __future__ import annotations

import re

# Стороны света: латиница и кириллица (С — север, Ю — юг, В — восток, З — запад)
_HEMISPHERES = {"N": ("lat", 1), "S": ("lat", -1), "E": ("lon", 1), "W": ("lon", -1),
                "С": ("lat", 1), "Ю": ("lat", -1), "В": ("lon", 1), "З": ("lon", -1)}
_H = "NSEWСЮВЗnsewсювз"
_NUM = r"\d{1,3}(?:[.,]\d+)?"

_COMPONENT = (
    rf"([{_H}])?\s*"                          # сторона света перед числом
    rf"([+\-−]?{_NUM})\s*"                    # градусы
    rf"(?:°\s*"
    rf"(?:({_NUM})\s*'\s*)?"                  # минуты
    rf"(?:({_NUM})\s*(?:\"|'')\s*)?"          # секунды
    rf")?"
    rf"([{_H}])?"                             # сторона света после числа
)
_PAIR = re.compile(rf"^\s*\(?\s*{_COMPONENT}\s*[,;/]?\s*{_COMPONENT}\s*\)?\s*$")
_LINK = re.compile(r"(?:[@=]|geo:)\s*([+-]?\d{1,2}\.\d+)\s*,\s*([+-]?\d{1,3}\.\d+)")

_QUOTES = str.maketrans({"′": "'", "’": "'", "‘": "'", "″": '"', "“": '"', "”": '"', "º": "°", "˚": "°"})


def _number(value: str | None) -> float:
    return float(value.replace(",", ".").replace("−", "-")) if value else 0.0


def _component(before, degrees, minutes, seconds, after) -> tuple[float, str | None, bool]:
    """Значение в десятичных градусах, ось по букве (lat/lon или None) и было ли «явное» оформление."""
    value = abs(_number(degrees)) + _number(minutes) / 60 + _number(seconds) / 3600
    sign = -1 if degrees.startswith(("-", "−")) else 1
    axis = None
    letter = (before or after or "").upper()
    if letter:
        axis, hemisphere_sign = _HEMISPHERES[letter]
        sign *= hemisphere_sign
    explicit = bool(letter or minutes or "." in degrees or "," in degrees)
    return sign * value, axis, explicit


def parse_coords(text: str) -> tuple[float, float] | None:
    """(широта, долгота) или None, если в тексте нет координат."""
    if not text or not any(ch.isdigit() for ch in text):
        return None
    text = text.strip().translate(_QUOTES)

    match = _PAIR.match(text)
    if match:
        first = _component(*match.groups()[:5])
        second = _component(*match.groups()[5:])
        # Числа без дробной части, градусов и букв («7 30») — скорее не координаты
        if not (first[2] or second[2]):
            return None
        (a, axis_a, _), (b, axis_b, _) = first, second
        lat, lon = (b, a) if axis_a == "lon" or axis_b == "lat" else (a, b)
    else:
        link = _LINK.search(text)
        if not link:
            return None
        lat, lon = float(link[1]), float(link[2])

    if not (-90 <= lat <= 90 and -180 <= lon <= 180) or (lat == 0 and lon == 0):
        return None
    return round(lat, 6), round(lon, 6)
