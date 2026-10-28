"""Тексты всех экранов бота (HTML-разметка). Строки на каждом языке — в bot/locales."""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime
from html import escape

from bot import locales, timeutil
from bot.db import User
from bot.locales import Locale
from bot.services import AirQuality, Forecast, Report

# Коды погоды WMO: (иконка днём, иконка ночью)
WMO_ICONS = {
    0: ("☀️", "🌙"), 1: ("🌤", "🌙"), 2: ("⛅️", "☁️"), 3: ("☁️", "☁️"),
    45: ("🌫", "🌫"), 48: ("🌫", "🌫"),
    51: ("🌦", "🌧"), 53: ("🌦", "🌧"), 55: ("🌧", "🌧"), 56: ("🌧", "🌧"), 57: ("🌧", "🌧"),
    61: ("🌦", "🌧"), 63: ("🌧", "🌧"), 65: ("🌧", "🌧"), 66: ("🌧", "🌧"), 67: ("🌧", "🌧"),
    71: ("🌨", "🌨"), 73: ("🌨", "🌨"), 75: ("❄️", "❄️"), 77: ("🌨", "🌨"),
    80: ("🌦", "🌧"), 81: ("🌧", "🌧"), 82: ("⛈", "⛈"),
    85: ("🌨", "🌨"), 86: ("❄️", "❄️"),
    95: ("⛈", "⛈"), 96: ("⛈", "⛈"), 99: ("⛈", "⛈"),
}

# Стрелка показывает, куда дует ветер (направление в API — откуда)
ARROWS = ["↓", "↙", "←", "↖", "↑", "↗", "→", "↘"]

# Верхние границы шкал; названия — в локалях
BEAUFORT = [0.3, 1.6, 3.4, 5.5, 8.0, 10.8, 13.9, 17.2, 20.8, 24.5, 28.5, 32.7]
UV_LIMITS = [3, 6, 8, 11]
EU_AQI_LIMITS = [20, 40, 60, 80, 100]


@dataclass(frozen=True)
class AqiLevel:
    icon: str
    name: str
    advice: str
    sport: str
    windows: str
    mask: str
    purifier: str


# Шкала US AQI — та же, что в приложении IQAir
AQI_LIMITS = [(50, "🟢"), (100, "🟡"), (150, "🟠"), (200, "🔴"), (300, "🟣"), (10**6, "🟤")]

# Подпись и суточная норма ВОЗ 2021 (мкг/м³)
POLLUTANTS = {
    "pm2_5": ("PM2.5", 15),
    "pm10": ("PM10", 45),
    "ozone": ("O₃", 100),
    "nitrogen_dioxide": ("NO₂", 25),
    "sulphur_dioxide": ("SO₂", 40),
    "carbon_monoxide": ("CO", 4000),
    "dust": (None, None),
}

HOURS_PER_PAGE = 12
HOURLY_PAGES = 4


# ── форматирование ──────────────────────────────────────────────────────────

def weather(loc: Locale, code: int | None, is_day: int | bool = True) -> tuple[str, str]:
    day_icon, night_icon = WMO_ICONS.get(code, ("🌡", "🌡"))
    return (day_icon if is_day else night_icon), loc["wmo"].get(code, "—")


def t(value: float | None) -> str:
    if value is None:
        return "—"
    r = round(value)
    return f"+{r}°" if r > 0 else f"−{-r}°" if r < 0 else "0°"


def hm(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def day_label(loc: Locale, d: date, today: date) -> str:
    if d == today:
        return f"{loc['today']}, {loc.day_month(d)}"
    if (d - today).days == 1:
        return f"{loc['tomorrow']}, {loc.day_month(d)}"
    return loc.date(d)


def direction(loc: Locale, degrees: float | None) -> tuple[str, str]:
    if degrees is None:
        return "", ""
    index = round(degrees / 45) % 8
    return loc["directions"][index], ARROWS[index]


def _scale(value: float, limits: list[float], names: list[str]) -> str:
    return next((name for limit, name in zip(limits, names) if value < limit), names[-1])


def wind(loc: Locale, speed: float | None, degrees: float | None, gusts: float | None = None) -> str:
    if speed is None:
        return "—"
    if round(speed) == 0:
        text = loc["calm"]
    else:
        name, arrow = direction(loc, degrees)
        force = _scale(speed, BEAUFORT, loc["beaufort"])
        text = f"<b>{round(speed)} {loc['ms']}</b> {name} {arrow} ({force})"
    if gusts is not None and round(gusts) > max(round(speed), 0):
        text += ", " + loc("gusts", g=round(gusts))
    return text


def pressure(loc: Locale, hpa: float | None) -> str:
    if hpa is None:
        return "—"
    return loc("pressure", mm=round(hpa * 0.750062), hpa=round(hpa))


def visibility(loc: Locale, meters: float) -> str:
    return f"{loc.num(meters / 1000)} {loc['km']}" if meters >= 1000 else f"{round(meters)} {loc['m']}"


def uv(loc: Locale, now: float | None, day_max: float | None) -> str:
    if now is None:
        return "—"
    if day_max is None:
        return f"{round(now)} ({_scale(now, UV_LIMITS, loc['uv_levels'])})"
    return loc("uv_now_max", now=round(now), max=round(day_max), level=_scale(day_max, UV_LIMITS, loc["uv_levels"]))


def duration(loc: Locale, seconds: float | None) -> str:
    if seconds is None:
        return "—"
    minutes = round(seconds / 60)
    return loc("duration", h=minutes // 60, m=minutes % 60)


def precipitation(loc: Locale, day: dict) -> str:
    total = day.get("precipitation_sum") or 0
    chance = day.get("precipitation_probability_max")
    if total >= 0.1:
        return loc("precip_sum", mm=loc.num(total, 1)) + (f" ({chance}%)" if chance is not None else "")
    if chance and chance >= 20:
        return loc("precip_chance", p=chance)
    return loc["no_precip"]


def aqi_level(loc: Locale, aqi: float) -> AqiLevel:
    index, icon = next((i, icon) for i, (limit, icon) in enumerate(AQI_LIMITS) if aqi <= limit)
    return AqiLevel(icon, *loc["aqi_levels"][index])


def eu_aqi_level(loc: Locale, value: float) -> str:
    names = loc["eu_aqi_levels"]
    return next((name for limit, name in zip(EU_AQI_LIMITS, names) if value <= limit), names[-1])


def concentration(loc: Locale, value: float) -> str:
    return loc.num(value, 0 if value >= 100 else 1)


def pollutant_label(loc: Locale, key: str) -> str:
    return POLLUTANTS.get(key, (key, None))[0] or loc["dust"]


def pollutant(loc: Locale, air: AirQuality, key: str) -> str:
    label = pollutant_label(loc, key)
    value = air.pollutants.get(key)
    return f"{label} · {concentration(loc, value)} {loc['ug']}" if value is not None else label


def place(loc: Locale, user: User) -> str:
    return escape(user.place or loc["my_place"])


# ── экраны ──────────────────────────────────────────────────────────────────

def welcome(lang: str, name: str) -> str:
    return locales.get(lang)("welcome", name=escape(name))


def greeting(lang: str, hour: int) -> str:
    loc = locales.get(lang)
    if 5 <= hour < 12:
        key = "greet_morning"
    elif 12 <= hour < 17:
        key = "greet_day"
    elif 17 <= hour < 23:
        key = "greet_evening"
    else:
        key = "greet_night"
    return f"{loc[key]} {loc['greet_suffix']}"


def saved_header(user: User) -> str:
    loc = locales.get(user.lang)
    text = loc["saved"]
    if user.notify_enabled:
        text += "\n" + loc("saved_schedule", time=user.notify_time)
    return text


def home(user: User, report: Report, header: str | None = None) -> str:
    loc = locales.get(user.lang)
    fc = report.forecast
    c = fc.current
    now = fc.local_now()
    today = fc.daily[0] if fc.daily else {}
    icon, desc = weather(loc, c.get("weather_code"), c.get("is_day", 1))

    lines = [header, ""] if header else []
    lines += [
        f"📍 <b>{place(loc, user)}</b>",
        f"<i>{loc.date(now)}, {hm(now)}</i>",
        "",
        f"{icon} <b>{t(c.get('temperature_2m'))}</b>  {desc}",
        loc("feels", t=t(c.get("apparent_temperature"))),
    ]
    if today:
        lines.append(loc(
            "today_range",
            min=t(today.get("temperature_2m_min")),
            max=t(today.get("temperature_2m_max")),
            precip=precipitation(loc, today),
        ))

    cloud = loc("clouds", c=loc.num(c.get("cloud_cover")))
    if c.get("visibility") is not None:
        cloud += loc("visibility", v=visibility(loc, c["visibility"]))
    lines += [
        "",
        loc("wind_line", wind=wind(loc, c.get("wind_speed_10m"), c.get("wind_direction_10m"), c.get("wind_gusts_10m"))),
        loc("humidity", h=loc.num(c.get("relative_humidity_2m")), dew=t(c.get("dew_point_2m"))),
        loc("pressure_line", p=pressure(loc, c.get("surface_pressure"))),
        cloud,
        loc("uv_line", uv=uv(loc, c.get("uv_index"), today.get("uv_index_max"))),
    ]
    if today.get("sunrise") and today.get("sunset"):
        lines.append(loc(
            "sun",
            rise=hm(today["sunrise"]),
            set=hm(today["sunset"]),
            len=duration(loc, today.get("daylight_duration")),
        ))

    periods = upcoming_periods(loc, fc, now)
    if periods:
        lines += ["", loc["next"], *periods]

    lines += ["", *air_summary(loc, report.air), "", schedule_line(user)]
    return "\n".join(lines)


def upcoming_periods(loc: Locale, fc: Forecast, now: datetime, count: int = 4) -> list[str]:
    result = []
    for h in fc.upcoming_hours(now):
        label = loc["periods"].get(h["time"].hour)
        if not label:
            continue
        icon, _ = weather(loc, h.get("weather_code"), h.get("is_day", 1))
        result.append(
            f"{label} {icon} <b>{t(h.get('temperature_2m'))}</b> · "
            f"💧{loc.num(h.get('precipitation_probability'))}% · "
            f"💨{loc.num(h.get('wind_speed_10m'))} {loc['ms']}"
        )
        if len(result) == count:
            break
    return result


def air_summary(loc: Locale, air: AirQuality | None) -> list[str]:
    if not air or air.aqi is None:
        return [loc["air_unavailable"]]
    level = aqi_level(loc, air.aqi)
    lines = [f"{level.icon} " + loc("air_short", aqi=round(air.aqi), level=level.name)]
    if air.main_pollutant:
        lines.append(loc("main_pollutant", p=pollutant(loc, air, air.main_pollutant)))
    lines.append(f"💡 {level.advice}")
    return lines


def schedule_line(user: User) -> str:
    loc = locales.get(user.lang)
    return loc("schedule_on", time=user.notify_time) if user.notify_enabled else loc["schedule_off"]


def hourly_pages(fc: Forecast) -> int:
    return max(1, min(HOURLY_PAGES, math.ceil(len(fc.upcoming_hours()) / HOURS_PER_PAGE)))


def hourly(user: User, fc: Forecast, page: int) -> str:
    loc = locales.get(user.lang)
    now = fc.local_now()
    hours = fc.upcoming_hours(now)[page * HOURS_PER_PAGE:(page + 1) * HOURS_PER_PAGE]
    lines = [loc["hourly_title"], f"📍 {place(loc, user)}", loc["hourly_legend"]]
    current_day = None
    for h in hours:
        day = h["time"].date()
        if day != current_day:
            current_day = day
            lines += ["", f"<b>{day_label(loc, day, now.date())}</b>"]
        icon, _ = weather(loc, h.get("weather_code"), h.get("is_day", 1))
        speed = h.get("wind_speed_10m")
        arrow = direction(loc, h.get("wind_direction_10m"))[1] if speed and round(speed) else ""
        rain = f"💧{loc.num(h.get('precipitation_probability'))}%"
        if (h.get("precipitation") or 0) >= 0.1:
            rain += f" {loc.num(h['precipitation'], 1)} {loc['mm']}"
        lines.append(
            f"<code>{hm(h['time'])}</code> {icon} <b>{t(h.get('temperature_2m'))}</b> "
            f"({t(h.get('apparent_temperature'))}) · {rain} · 💨{loc.num(speed)} {loc['ms']} {arrow}".rstrip()
        )
    return "\n".join(lines)


def daily(user: User, fc: Forecast) -> str:
    loc = locales.get(user.lang)
    today = fc.local_now().date()
    lines = [loc["daily_title"], f"📍 {place(loc, user)}"]
    for d in fc.daily:
        icon, desc = weather(loc, d.get("weather_code"))
        name, arrow = direction(loc, d.get("wind_direction_10m_dominant"))
        lines += [
            "",
            f"<b>{day_label(loc, d['time'], today)}</b> — {icon} {desc}",
            f"🌡 {t(d.get('temperature_2m_min'))} … {t(d.get('temperature_2m_max'))} · {precipitation(loc, d)}",
            loc(
                "daily_wind", dir=name, arrow=arrow,
                max=loc.num(d.get("wind_speed_10m_max")),
                g=loc.num(d.get("wind_gusts_10m_max")),
                uv=loc.num(d.get("uv_index_max")),
            ),
        ]
    return "\n".join(lines)


def air_details(user: User, air: AirQuality | None) -> str:
    loc = locales.get(user.lang)
    lines = [loc["air_title"], f"📍 {place(loc, user)}", ""]
    if not air or air.aqi is None:
        lines.append(loc["air_na"])
        return "\n".join(lines)

    level = aqi_level(loc, air.aqi)
    lines.append(f"{level.icon} " + loc("aqi_line", aqi=round(air.aqi), level=level.name))
    if air.main_pollutant:
        lines.append(loc("main_pollutant", p=f"<b>{pollutant(loc, air, air.main_pollutant)}</b>"))
    if air.eu_aqi is not None:
        lines.append(loc("eu_line", v=round(air.eu_aqi), level=eu_aqi_level(loc, air.eu_aqi)))
    source = air.source + (f" · {escape(air.station)}" if air.station else "")
    lines.append(f"<i>{loc('source', s=source)}</i>")

    measured = [(k, v) for k, v in air.pollutants.items() if v is not None]
    if measured:
        lines += ["", loc["pollutants_title"]]
        for key, value in measured:
            norm = POLLUTANTS[key][1]
            mark = ""
            if norm:
                ratio = value / norm
                mark = f" ⚠️ ×{loc.num(ratio, 1)}" if ratio > 1 else " ✅"
            title = loc["pollutants"].get(key)
            title = f" {title}" if title else ""
            lines.append(
                f"• <b>{pollutant_label(loc, key)}</b>{title} — {concentration(loc, value)} {loc['ug']}{mark}"
            )

    lines += [
        "",
        loc["advice_title"],
        loc("sport", v=level.sport),
        loc("windows", v=level.windows),
        loc("mask", v=level.mask),
        loc("purifier", v=level.purifier),
        f"💡 {level.advice}",
    ]

    now = air.local_now().replace(minute=0, second=0, microsecond=0)
    upcoming = [
        h for h in air.hourly
        if h["time"] > now and h["time"].hour % 3 == 0 and h.get("us_aqi") is not None
    ][:8]
    if upcoming:
        cells = [f"{hm(h['time'])} {aqi_level(loc, h['us_aqi']).icon}{round(h['us_aqi'])}" for h in upcoming]
        lines += ["", loc["aqi_forecast"]]
        lines += ["  ".join(cells[i:i + 4]) for i in range(0, len(cells), 4)]

    lines += ["", loc["scale"]]
    return "\n".join(lines)


def settings(user: User) -> str:
    loc = locales.get(user.lang)
    time_line = loc("s_time", time=user.notify_time)
    if user.tz:
        time_line += f" <i>({escape(user.tz)})</i>"
    lines = [
        loc["settings_title"],
        "",
        loc("s_place", p=escape(user.place) if user.place else loc["s_place_none"]),
        time_line,
        loc("s_notify", state=loc["on"] if user.notify_enabled else loc["off"]),
    ]
    upcoming = timeutil.next_send(user)
    if upcoming:
        today = timeutil.local_now(user.tz).date()
        when = loc["today_l"] if upcoming.date() == today else loc["tomorrow_l"]
        lines.append(loc("s_next", when=when, time=hm(upcoming)))
    lines.append(loc("s_lang", name=loc["lang_name"]))
    return "\n".join(lines)


def language(lang: str) -> str:
    return locales.get(lang)["lang_title"]


def time_hours(user: User, error: bool = False) -> str:
    loc = locales.get(user.lang)
    current = loc("time_current", time=user.notify_time)
    if user.tz:
        current += loc("time_local", tz=escape(user.tz))
    lines = [loc["time_title"], "", current, loc["pick_hour"], "", loc["time_hint"]]
    if error:
        lines.insert(0, loc["time_error"])
    return "\n".join(lines)


def time_minutes(lang: str, hour: int) -> str:
    loc = locales.get(lang)
    return f"{loc['time_title']}\n\n{loc('time_hour', h=f'{hour:02d}')}\n{loc['pick_minutes']}"


def time_saved(user: User) -> str:
    return locales.get(user.lang)("time_saved", time=user.notify_time) + "\n\n" + settings(user)


def location_prompt(lang: str) -> str:
    return locales.get(lang)["location_prompt"]


def location_keyboard_hint(lang: str) -> str:
    return locales.get(lang)["location_keyboard_hint"]


def searching(lang: str, query: str) -> str:
    return locales.get(lang)("searching", q=escape(query))


def locating(lang: str) -> str:
    return locales.get(lang)["locating"]


def search_results(lang: str, query: str) -> str:
    return locales.get(lang)("search_results", q=escape(query))


def not_found(lang: str, query: str) -> str:
    return locales.get(lang)("not_found", q=escape(query))


def error(lang: str) -> str:
    return locales.get(lang)["error"]
