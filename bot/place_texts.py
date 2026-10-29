"""Тексты избранных мест и поездок."""
from __future__ import annotations

from datetime import date
from html import escape

from bot import locales
from bot.db import SavedPlace, User
from bot.locales import Locale


def _span(loc: Locale, start: str, end: str) -> str:
    a, b = date.fromisoformat(start), date.fromisoformat(end)
    return loc.day_month(a) if a == b else f"{loc.day_month(a)} — {loc.day_month(b)}"


def trip_line(loc: Locale, user: User, dest: SavedPlace | None) -> str | None:
    if not (dest and user.trip_from and user.trip_to):
        return None
    key = "pl_trip_on" if user.trip_on else "pl_trip_planned"
    return loc(key, name=escape(dest.name), span=_span(loc, user.trip_from, user.trip_to))


def places(lang: str, user: User, items: list[SavedPlace], dest: SavedPlace | None, error: str | None = None) -> str:
    loc = locales.get(lang)
    lines = [loc[error], ""] if error else []
    lines += [loc["pl_title"], "", loc["pl_intro"], "",
              loc("pl_now", place=escape(user.place) if user.place else loc["s_place_none"])]
    trip = trip_line(loc, user, dest)
    if trip:
        lines.append(trip)
    if not items:
        lines += ["", loc["pl_empty"]]
    return "\n".join(lines)


def trip_dest(lang: str, has_places: bool) -> str:
    loc = locales.get(lang)
    return "\n".join([loc["pl_trip_title"], "", loc["pl_trip_intro"], "",
                      loc["pl_trip_where"] if has_places else loc["pl_trip_need_place"]])


def trip_from(lang: str, dest: SavedPlace) -> str:
    loc = locales.get(lang)
    return "\n".join([loc["pl_trip_title"], loc("pl_trip_dest", name=escape(dest.name)), "", loc["pl_trip_when"]])


def trip_len(lang: str, dest: SavedPlace, start: date) -> str:
    loc = locales.get(lang)
    return "\n".join([loc["pl_trip_title"], loc("pl_trip_dest", name=escape(dest.name)),
                      loc("pl_trip_start", day=loc.date(start)), "", loc["pl_trip_days"]])


def trip_started(lang: str, dest: SavedPlace, user: User) -> str:
    loc = locales.get(lang)
    return loc("pl_trip_started", name=escape(dest.name), span=_span(loc, user.trip_from, user.trip_to))


def trip_ended(lang: str, home: SavedPlace | None) -> str:
    loc = locales.get(lang)
    return loc("pl_trip_ended", name=escape(home.name)) if home else loc["pl_trip_ended_nohome"]
