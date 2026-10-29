"""Тексты перевалов (погода на дороге) и горнолыжных курортов (снег и погода наверху трасс)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from html import escape

from bot import locales
from bot.locales import Locale
from bot.services.mountain import MountainForecast
from bot.texts import day_label, hm, t, weather

ROAD_ICONS = {"snow": "❄️", "ice": "🧊", "rain": "🌧", "fog": "🌫", "wind": "💨"}
BAD_ROAD = {"snow", "ice"}
ROAD_AHEAD = 24
LIFT_HOURS = range(9, 18)
POWDER_CM = 10           # столько свежего снега за ночь — день для катания по целине
LIFT_WIND = 15           # м/с наверху — подъёмники могут остановить
SLUSH_TEMP = 3           # теплее внизу днём — снег подтаивает


@dataclass(frozen=True)
class Pass:
    key: str
    name: str
    road: str
    lat: float
    lon: float
    ele: int


@dataclass(frozen=True)
class Resort:
    key: str
    name: str
    lat: float
    lon: float
    base: int
    top: int


def passes(lang: str, rows: list[tuple]) -> list[Pass]:
    i = ("ru", "uz", "en").index(locales.get(lang).code)
    return [Pass(r[0], r[1 + i], r[4 + i], r[7], r[8], r[9]) for r in rows]


def resorts(lang: str, rows: list[tuple]) -> list[Resort]:
    i = ("ru", "uz", "en").index(locales.get(lang).code)
    return [Resort(r[0], r[1 + i], r[4], r[5], r[6], r[7]) for r in rows]


def _flags(loc: Locale, flags: list[str]) -> str:
    return ", ".join(f"{ROAD_ICONS[f]} {loc['road_' + f]}" for f in flags)


# ── перевалы ────────────────────────────────────────────────────────────────

def road_status(loc: Locale, fc: MountainForecast) -> tuple[str, str]:
    """(иконка, коротко): что на дороге сейчас или в ближайшие сутки."""
    hours = fc.upcoming()[:ROAD_AHEAD + 1]
    now = fc.road(hours[0]) if hours else []
    if set(now) & BAD_ROAD:
        return "❌", _flags(loc, now)
    for h in hours[1:]:
        flags = fc.road(h)
        if flags:
            return "⚠️", loc("road_by", what=_flags(loc, flags), time=hm(h["time"]))
    if now:
        return "⚠️", _flags(loc, now)
    return "✅", loc["road_clear"]


def passes_list(lang: str, items: list[tuple[Pass, MountainForecast | None]]) -> str:
    loc = locales.get(lang)
    lines = [loc["road_title"], loc["road_intro"], ""]
    for p, fc in items:
        if fc is None:
            lines += [f"❔ <b>{escape(p.name)}</b> · {p.ele} {loc['m']} — {loc['road_na']}", f"└ {escape(p.road)}"]
            continue
        icon, status = road_status(loc, fc)
        temp = t(fc.summit(fc.hour()).temp)
        lines += [f"{icon} <b>{escape(p.name)}</b> · {p.ele} {loc['m']} · {temp} — {status}", f"└ {escape(p.road)}"]
    lines += ["", loc["road_note"]]
    return "\n".join(lines)


def pass_detail(lang: str, p: Pass, fc: MountainForecast) -> str:
    loc = locales.get(lang)
    now = fc.local_now()
    row = fc.hour(now)
    c = fc.summit(row)
    icon, desc = weather(loc, c.weather_code, c.is_day)
    status_icon, status = road_status(loc, fc)
    lines = [
        f"🛣 <b>{escape(p.name)}</b> · {p.ele} {loc['m']}",
        escape(p.road),
        "",
        loc("road_now", time=hm(row["time"])),
        f"{icon} {desc} · <b>{t(c.temp)}</b> · 💨 {loc.num(c.wind)} {loc['ms']}",
        f"{status_icon} {status}",
        "",
        loc["road_next"],
    ]
    for h in fc.upcoming(now)[3:ROAD_AHEAD + 1:3]:
        hc = fc.summit(h)
        flags = fc.road(h)
        cell = f"<code>{hm(h['time'])}</code> {t(hc.temp)} 💨{loc.num(hc.wind)}"
        lines.append(cell + (f" · {_flags(loc, flags)}" if flags else ""))
    today = now.date()
    lines += ["", loc["road_days"]]
    for d in sorted({h["time"].date() for h in fc.upcoming(now)})[:3]:
        rows = [h for h in fc.upcoming(now) if h["time"].date() == d]
        temps = [x.temp for x in (fc.summit(h) for h in rows) if x.temp is not None]
        flags = sorted({f for h in rows for f in fc.road(h)}, key=list(ROAD_ICONS).index)
        text = f"<b>{day_label(loc, d, today)}</b>: {t(min(temps, default=None))}…{t(max(temps, default=None))}"
        lines.append(text + (f" · {_flags(loc, flags)}" if flags else f" · {loc['road_clear']}"))
    lines += ["", loc["road_note"]]
    return "\n".join(lines)


# ── горнолыжка ──────────────────────────────────────────────────────────────

@dataclass
class SkiNow:
    day: float           # см свежего снега наверху за сутки
    three: float         # за 3 дня
    coming: float        # ожидается за 2 дня
    top: float | None
    base: float | None
    wind: float | None

    @property
    def powder(self) -> bool:
        return self.day >= POWDER_CM


def ski_now(r: Resort, fc: MountainForecast) -> SkiNow:
    now = fc.local_now()
    row = fc.hour(now)
    top, base = fc.at(row, r.top), fc.at(row, r.base)
    return SkiNow(
        day=fc.snow_sum(now - timedelta(hours=24), now),
        three=fc.snow_sum(now - timedelta(hours=72), now),
        coming=fc.snow_sum(now, now + timedelta(hours=48)),
        top=top.temp, base=base.temp, wind=top.wind,
    )


def _ski_lines(loc: Locale, s: SkiNow) -> list[str]:
    lines = [loc("ski_snow", day=round(s.day), three=round(s.three))
             + (loc("ski_coming", cm=round(s.coming)) if s.coming >= 1 else "")]
    lines.append(loc("ski_temp", top=t(s.top), base=t(s.base), wind=loc.num(s.wind)))
    if s.powder:
        lines.append(loc["ski_powder"])
    if (s.wind or 0) >= LIFT_WIND:
        lines.append(loc["ski_lifts"])
    return lines


def ski_list(lang: str, items: list[tuple[Resort, MountainForecast | None]]) -> str:
    loc = locales.get(lang)
    lines = [loc["ski_title"], loc["ski_intro"]]
    for r, fc in items:
        lines += ["", f"⛷ <b>{escape(r.name)}</b> · {r.base}–{r.top} {loc['m']}"]
        lines += _ski_lines(loc, ski_now(r, fc)) if fc else [loc["road_na"]]
    lines += ["", loc["ski_note"]]
    return "\n".join(lines)


def resort_detail(lang: str, r: Resort, fc: MountainForecast, subscribed: bool) -> str:
    loc = locales.get(lang)
    now = fc.local_now()
    lines = [f"⛷ <b>{escape(r.name)}</b> · {r.base}–{r.top} {loc['m']}", "", *_ski_lines(loc, ski_now(r, fc)), "",
             loc["ski_days"]]
    for d in sorted({h["time"].date() for h in fc.upcoming(now)})[:3]:
        rows = [h for h in fc.upcoming(now) if h["time"].date() == d and h["time"].hour in LIFT_HOURS]
        if not rows:
            continue
        tops = [fc.at(h, r.top) for h in rows]
        bases = [fc.at(h, r.base) for h in rows]
        snow = sum(x.precip for x in tops if x.phase in ("snow", "sleet"))
        wind = max((x.wind or 0 for x in tops), default=0)
        base_max = max((x.temp for x in bases if x.temp is not None), default=None)
        fog = sum(x.in_cloud for x in tops)
        notes = []
        if snow >= 1:
            notes.append(loc("ski_d_snow", cm=round(snow)))
        if wind >= LIFT_WIND:
            notes.append(loc("ski_d_wind", v=round(wind)))
        if fog >= 4:
            notes.append(loc["ski_d_fog"])
        if base_max is not None and base_max >= SLUSH_TEMP:
            notes.append(loc["ski_d_slush"])
        if any(x.phase == "rain" for x in bases):
            notes.append(loc["ski_d_rain"])
        icon = "❌" if wind >= LIFT_WIND + 5 else "⚠️" if notes and not (len(notes) == 1 and snow >= 1) else "✅"
        temps = [x.temp for x in tops if x.temp is not None]
        lines.append(
            f"{icon} <b>{day_label(loc, d, now.date())}</b>: "
            + loc("ski_d_temp", lo=t(min(temps, default=None)), hi=t(max(temps, default=None)))
            + (f" · {', '.join(notes)}" if notes else "")
        )
    lines += ["", loc["ski_sub_on" if subscribed else "ski_sub_off"], loc["ski_note"]]
    return "\n".join(lines)


def powder_alert(lang: str, r: Resort, s: SkiNow) -> str:
    loc = locales.get(lang)
    return "\n".join([loc("ski_alert", name=escape(r.name), cm=round(s.day)), "", *_ski_lines(loc, s)])
