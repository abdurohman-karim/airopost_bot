"""Тексты GPX-маршрутов: сводка трека и погода по пути на время прохождения каждой точки."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from html import escape

from bot import locales
from bot.gpx import Leg, Track
from bot.locales import Locale
from bot.services.mountain import CAUTION_WIND, Conditions
from bot.texts import duration, hm, t, weather

PHASE_ICON = {"snow": "❄️", "sleet": "🌨", "rain": "🌧"}
COLD_FEELS = -10


@dataclass
class Stop:
    leg: Leg
    at: datetime                 # местное время прохождения
    c: Conditions | None         # None — на это время прогноза ещё нет
    thunder: bool


def _hours(loc: Locale, hours: float) -> str:
    return duration(loc, max(10, round(hours * 6) * 10) * 60)


def start_label(loc: Locale, code: str, dt: datetime) -> str:
    if code == "now":
        return loc["rt_now"]
    day = loc["tomorrow"] if code.startswith("t") else loc["weekdays"][dt.weekday()]
    return f"{day} {hm(dt)}"


def summary(lang: str, tr: Track, error: str | None = None) -> str:
    loc = locales.get(lang)
    lines = [loc[error], ""] if error else []
    lines += [
        f"🗺 <b>{escape(tr.name)}</b>",
        loc("rt_stats", km=loc.num(tr.km, 1), gain=round(tr.gain), loss=round(tr.loss)),
        loc("rt_heights", low=round(tr.low.ele), top=round(tr.top.ele), time=_hours(loc, tr.hours)),
        loc["rt_pace"],
        "",
        loc["rt_pick_start"],
    ]
    return "\n".join(lines)


def plan(lang: str, tr: Track, stops: list[Stop], sunset: datetime | None) -> str:
    loc = locales.get(lang)
    start, finish = stops[0].at, stops[0].at + timedelta(hours=tr.hours)
    head = loc("rt_when", date=loc.date(start), start=hm(start), finish=hm(finish))
    if sunset:
        head += loc("rt_sunset", time=hm(sunset))
    lines = [
        f"🗺 <b>{escape(tr.name)}</b> · " + loc("rt_stats", km=loc.num(tr.km, 1), gain=round(tr.gain), loss=round(tr.loss)),
        head, "", loc["rt_weather"],
    ]
    top = tr.top
    for s in stops:
        mark = " ⛰" if s.leg is top else ""
        when = hm(s.at) if s.at.date() == start.date() else f"{loc['weekdays'][s.at.weekday()]} {hm(s.at)}"
        cell = f"<code>{when}</code> {loc.num(s.leg.km, 1)} {loc['km']} · {round(s.leg.ele)} {loc['m']}{mark}"
        if s.c is None:
            lines.append(f"{cell} · {loc['rt_no_fc']}")
            continue
        icon, _ = weather(loc, s.c.weather_code, s.c.is_day)
        cell += f" · {icon} <b>{t(s.c.temp)}</b> ({t(s.c.feels)}) 💨{loc.num(s.c.wind)}"
        if s.c.phase:
            cell += f" {PHASE_ICON[s.c.phase]}"
        if s.c.in_cloud:
            cell += " 🌫"
        if s.thunder:
            cell += " ⚡️"
        lines.append(cell)

    warnings = []
    if sunset and finish > sunset:
        warnings.append(loc("rt_w_dark", time=hm(sunset - timedelta(hours=tr.hours))))
    known = [s for s in stops if s.c]
    storm = next((s for s in known if s.thunder), None)
    if storm:
        warnings.append(loc("rt_w_storm", time=hm(storm.at), ele=round(storm.leg.ele)))
    windy = max(known, key=lambda s: s.c.wind or 0, default=None)
    if windy and (windy.c.wind or 0) >= CAUTION_WIND:
        warnings.append(loc("rt_w_wind", v=round(windy.c.wind), ele=round(windy.leg.ele), time=hm(windy.at)))
    wet = next((s for s in known if s.c.phase), None)
    if wet:
        warnings.append(loc("rt_w_precip", what=loc["m_" + wet.c.phase], ele=round(wet.leg.ele), time=hm(wet.at)))
    cold = min(known, key=lambda s: s.c.feels if s.c.feels is not None else 99, default=None)
    if cold and cold.c.feels is not None and cold.c.feels <= COLD_FEELS:
        warnings.append(loc("rt_w_cold", t=t(cold.c.feels), ele=round(cold.leg.ele)))
    if len(known) < len(stops):
        warnings.append(loc["rt_w_partial"])
    lines.append("")
    lines += [loc["m_warnings"], *(f"• {w}" for w in warnings)] if warnings else [loc["rt_all_good"]]
    lines += ["", loc["rt_note"]]
    return "\n".join(lines)


def routes_list(lang: str, has_routes: bool) -> str:
    loc = locales.get(lang)
    return "\n".join([loc["rt_title"], "", loc["rt_intro"], "", loc["rt_saved"] if has_routes else loc["rt_empty"]])


def reading(lang: str) -> str:
    return locales.get(lang)["rt_reading"]
