"""Тексты горных экранов: вершина, профиль высот, часы, окна для восхождения, маршрут."""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from html import escape

from bot import locales
from bot.catalog import REGIONS
from bot.db import Peak
from bot.locales import Locale
from bot.services.mountain import (
    CAUTION_CAPE, CAUTION_WIND, STORM_CAPE, Conditions, DayOutlook, Here, MountainForecast,
    PeakResult, distance_km, route_bands, summit_bands,
)
from bot.texts import day_label, direction, duration, hm, t, weather

RATING_ICON = {"good": "✅", "caution": "⚠️", "bad": "❌"}
PHASE_ICON = {"snow": "❄️", "sleet": "🌨", "rain": "🌧"}
UV_PER_KM = 0.08          # УФ растёт примерно на 8 % на каждый километр высоты
PROFILE_STEPS = 24        # профиль на 72 часа вперёд с шагом 3 часа
HOURS_PER_PAGE = 12
CATALOG_PER_PAGE = 8
HOURLY_PAGES = 6
ROUTE_AHEAD = 6           # часов вперёд для предупреждений на маршруте
COLD_WARNING = -20


def _ele(loc: Locale, value: float) -> str:
    return f"{round(value)} {loc['m']}"


def _phase(loc: Locale, phase: str | None) -> str:
    return loc[f"m_{phase}"] if phase else ""


def peak_header(loc: Locale, peak: Peak) -> str:
    return f"⛰ <b>{escape(peak.name)}</b> · {_ele(loc, peak.ele)}"


def result_label(loc: Locale, r: PeakResult) -> str:
    parts = [r.name]
    if r.ele:
        parts.append(_ele(loc, r.ele))
    if r.country:
        parts.append(r.country)
    return " · ".join(parts)


# ── список и добавление ─────────────────────────────────────────────────────

def mountains(lang: str, peaks: list[Peak]) -> str:
    loc = locales.get(lang)
    return "\n".join([
        loc["m_title"], "", loc["m_intro"], "",
        loc["m_saved"] if peaks else loc["m_empty"], loc["m_private_note"],
    ])


def region_of(p: Peak) -> str:
    return p.region if p.region in REGIONS else "community"


def catalog_regions(peaks: list[Peak]) -> list[tuple[str, int]]:
    """Регионы каталога в порядке REGIONS с числом вершин, пустые пропускаются."""
    counts = [(region, sum(1 for p in peaks if region_of(p) == region)) for region in REGIONS]
    return [(region, n) for region, n in counts if n]


def region_peaks(peaks: list[Peak], region: str) -> list[Peak]:
    return sorted((p for p in peaks if region_of(p) == region), key=lambda p: -p.ele)


def catalog_pages(peaks: list[Peak]) -> int:
    return max(1, math.ceil(len(peaks) / CATALOG_PER_PAGE))


def catalog(lang: str, peaks: list[Peak]) -> str:
    loc = locales.get(lang)
    return "\n".join([loc["m_catalog_title"], "", loc["m_catalog_intro"]])


def catalog_region(lang: str, region: str, peaks: list[Peak], page: int) -> str:
    loc = locales.get(lang)
    lines = [loc["m_catalog_title"], f"<b>{loc['region_' + region]}</b>"]
    pages = catalog_pages(peaks)
    if pages > 1:
        lines += ["", loc("m_catalog_page", p=page + 1, n=pages)]
    return "\n".join(lines)


def status_line(lang: str, p: Peak) -> str:
    loc = locales.get(lang)
    if p.public:
        return loc["st_community"] if p.author_id else loc["st_catalog"]
    return loc[f"st_{p.status}"] if p.status else loc["st_private"]


def publish_confirm(lang: str, p: Peak) -> str:
    return locales.get(lang)("m_publish_confirm", name=escape(p.name), ele=p.ele, lat=f"{p.lat:.5f}", lon=f"{p.lon:.5f}")


def admin_request(lang: str, request_id: int, name: str, ele: int, lat: float, lon: float, author: str) -> str:
    map_url = f"https://www.openstreetmap.org/?mlat={lat:.5f}&mlon={lon:.5f}#map=15/{lat:.5f}/{lon:.5f}"
    return locales.get(lang)(
        "a_request", id=request_id, name=escape(name), ele=ele, lat=f"{lat:.5f}", lon=f"{lon:.5f}",
        map=map_url, author=author,
    )


def add_prompt(lang: str) -> str:
    loc = locales.get(lang)
    return f"{loc['m_add_prompt']}\n\n{loc['coords_hint']}"


def searching(lang: str, query: str) -> str:
    return locales.get(lang)("m_searching", q=escape(query))


def results(lang: str, query: str) -> str:
    return locales.get(lang)("m_results", q=escape(query))


def not_found(lang: str, query: str) -> str:
    return locales.get(lang)("m_not_found", q=escape(query))


def point_name(lang: str, lat: float, lon: float) -> str:
    return locales.get(lang)("m_point_name", lat=f"{lat:.3f}", lon=f"{lon:.3f}")


def edit_prompt(lang: str, peak: Peak, error: bool = False) -> str:
    loc = locales.get(lang)
    text = loc("m_ele_prompt", name=escape(peak.name), ele=peak.ele)
    return (loc["m_ele_error"] + "\n" + text) if error else text


def delete_confirm(lang: str, peak: Peak) -> str:
    return locales.get(lang)("m_delete_confirm", name=escape(peak.name))


# ── фрагменты ───────────────────────────────────────────────────────────────

def _reasons(loc: Locale, reasons: list[tuple[str, dict]]) -> str:
    parts = []
    for key, params in reasons:
        if key == "r_precip":
            parts.append(loc(key, phase=_phase(loc, params["phase"]) or loc["m_rain"], mm=loc.num(params["mm"], 1)))
        elif key == "r_cold":
            parts.append(loc(key, t=t(params["t"])))
        else:
            parts.append(loc(key, **params) if params else loc[key])
    return ", ".join(parts)


def _day_line(loc: Locale, o: DayOutlook, today) -> str:
    text = f"{RATING_ICON[o.rating]} <b>{day_label(loc, o.day, today)}</b> — {loc['m_' + o.rating]}"
    if o.reasons:
        text += f": {_reasons(loc, o.reasons)}"
    return text


def _storm_level(loc: Locale, fc: MountainForecast, hours: list[dict]) -> str:
    levels = loc["m_storm_levels"]
    if any(fc.thunder(h) for h in hours):
        return levels[2]
    cape = max((h.get("cape") or 0 for h in hours), default=0)
    return levels[2] if cape >= STORM_CAPE else levels[1] if cape >= CAUTION_CAPE else levels[0]


def _precip(loc: Locale, c: Conditions) -> str:
    if c.phase:
        return loc(
            "m_precip", icon=PHASE_ICON[c.phase], phase=_phase(loc, c.phase).capitalize(),
            mm=loc.num(c.precip, 1), p=c.precip_prob or 0,
        )
    return loc("m_no_precip", p=c.precip_prob or 0)


def _summit_now(loc: Locale, fc: MountainForecast, row: dict) -> list[str]:
    c = fc.summit(row)
    icon, desc = weather(loc, c.weather_code, c.is_day)
    name, arrow = direction(loc, c.wind_dir)
    lines = [
        loc("m_now", time=hm(c.time)),
        f"{icon} {desc}",
        loc("m_temp", t=t(c.temp), feels=t(c.feels)),
        loc("m_wind", v=loc.num(c.wind), dir=name, arrow=arrow),
        _precip(loc, c),
    ]
    if c.in_cloud:
        lines.append(loc["m_in_cloud"])
    fl = row.get("freezing_level_height")
    if fl is not None:
        lines.append(loc("m_fl", h=round(fl)) + (loc["m_fl_below"] if fl < fc.elevation else loc["m_fl_above"]))
    if fc.thunder(row):
        lines.append(loc["m_thunder_now"])
    else:
        lines.append(loc("m_storm", level=_storm_level(loc, fc, fc.upcoming()[:12])))
    return lines


def _sun_and_uv(loc: Locale, fc: MountainForecast) -> list[str]:
    today = fc.day(fc.local_now().date())
    if not today:
        return []
    lines = []
    uv = today.get("uv_index_max")
    if uv is not None and uv >= 3:
        lines.append(loc("m_uv", uv=round(uv * (1 + UV_PER_KM * fc.elevation / 1000))))
    if today.get("sunrise") and today.get("sunset"):
        lines.append(loc("m_sun", rise=hm(today["sunrise"]), set=hm(today["sunset"])))
    return lines


def _band_row(loc: Locale, c: Conditions, mark: str = "") -> str:
    _, arrow = direction(loc, c.wind_dir)
    text = (
        f"<code>{round(c.elevation):>4} {loc['m']}</code>{mark} <b>{t(c.temp)}</b> ({t(c.feels)}) · "
        f"💨{loc.num(c.wind)} {arrow}"
    )
    if c.phase:
        text += f" · {PHASE_ICON[c.phase]}{loc.num(c.precip, 1)}"
    if c.in_cloud:
        text += " 🌫"
    return text


def _profile_rows(
    loc: Locale, fc: MountainForecast, row: dict, bands: list[int], you: int | None = None,
) -> list[str]:
    """Строки профиля сверху вниз; нулевая изотерма вставляется между соседними высотами."""
    fl = row.get("freezing_level_height")
    lines, fl_done = [], fl is None
    for i, z in enumerate(bands):
        if not fl_done and fl >= z:
            lines.append(loc("m_fl_row", h=round(fl)))
            fl_done = True
        mark = " ⛰" if i == 0 else (loc["m_you"] if z == you else "")
        lines.append(_band_row(loc, fc.at(row, z), mark))
    if not fl_done:
        lines.append(loc("m_fl_row", h=round(fl)))
    return lines


def _updated(loc: Locale, fc: MountainForecast) -> str:
    now = fc.local_now()
    return loc("m_updated", time=f"{loc.date(now)}, {hm(now)}", ele=round(fc.elevation))


# ── экраны вершины ──────────────────────────────────────────────────────────

def peak(lang: str, p: Peak, fc: MountainForecast, header: str | None = None) -> str:
    loc = locales.get(lang)
    today = fc.local_now().date()
    lines = [header, ""] if header else []
    lines += [peak_header(loc, p), f"📍 {p.lat:.4f}, {p.lon:.4f}", status_line(lang, p), ""]
    lines += _summit_now(loc, fc, fc.hour())
    lines += _sun_and_uv(loc, fc)
    outlook = fc.outlook()[:3]
    if outlook:
        lines += ["", loc["m_windows"], *(_day_line(loc, o, today) for o in outlook)]
    lines += ["", _updated(loc, fc)]
    return "\n".join(lines)


def profile_time(fc: MountainForecast, step: int) -> datetime:
    return fc.local_now() + timedelta(hours=3 * step)


def profile(lang: str, p: Peak, fc: MountainForecast, step: int) -> str:
    loc = locales.get(lang)
    row = fc.hour(profile_time(fc, step))
    when = row["time"]
    lines = [
        loc("m_profile_title", name=escape(p.name)),
        f"<i>{day_label(loc, when.date(), fc.local_now().date())}, {hm(when)}</i>",
        loc["m_profile_legend"],
        "",
        *_profile_rows(loc, fc, row, summit_bands(p.ele)),
        "",
        loc["m_profile_note"],
    ]
    return "\n".join(lines)


def hourly_pages(fc: MountainForecast) -> int:
    return max(1, min(HOURLY_PAGES, math.ceil(len(fc.upcoming()) / HOURS_PER_PAGE)))


def _hour_row(loc: Locale, fc: MountainForecast, h: dict) -> str:
    c = fc.summit(h)
    icon, _ = weather(loc, c.weather_code, c.is_day)
    _, arrow = direction(loc, c.wind_dir)
    text = f"<code>{hm(c.time)}</code> {icon} <b>{t(c.temp)}</b> ({t(c.feels)}) · 💨{loc.num(c.wind)} {arrow}"
    if c.phase:
        text += f" · {PHASE_ICON[c.phase]}{loc.num(c.precip, 1)}"
    elif (c.precip_prob or 0) >= 20:
        text += f" · 💧{c.precip_prob}%"
    if c.in_cloud:
        text += " 🌫"
    if fc.thunder(h):
        text += " ⚡️"
    return text


def hourly(lang: str, p: Peak, fc: MountainForecast, page: int) -> str:
    loc = locales.get(lang)
    today = fc.local_now().date()
    hours = fc.upcoming()[page * HOURS_PER_PAGE:(page + 1) * HOURS_PER_PAGE]
    lines = [loc("m_hourly_title", name=escape(p.name), ele=p.ele), loc["m_hourly_legend"]]
    current_day = None
    for h in hours:
        if h["time"].date() != current_day:
            current_day = h["time"].date()
            lines += ["", f"<b>{day_label(loc, current_day, today)}</b>"]
        lines.append(_hour_row(loc, fc, h))
    return "\n".join(lines)


def outlook(lang: str, p: Peak, fc: MountainForecast) -> str:
    loc = locales.get(lang)
    today = fc.local_now().date()
    lines = [loc("m_outlook_title", name=escape(p.name))]
    for o in fc.outlook():
        if o.precip >= 0.1 and o.phase:
            precip = f"{PHASE_ICON[o.phase]} {_phase(loc, o.phase)} {loc.num(o.precip, 1)} {loc['mm']}"
        else:
            precip = loc["m_precip_none"]
        if o.fl_min is not None:
            precip += loc("m_outlook_fl", lo=round(o.fl_min), hi=round(o.fl_max))
        lines += [
            "",
            _day_line(loc, o, today),
            loc("m_outlook_day", tmin=t(o.t_min), tmax=t(o.t_max), feels=t(o.feels_min), wind=loc.num(o.wind_max)),
            precip,
        ]
    lines += ["", loc["m_outlook_note"]]
    return "\n".join(lines)


# ── маршрут ─────────────────────────────────────────────────────────────────

def route_prompt(lang: str, p: Peak) -> str:
    loc = locales.get(lang)
    return f"{loc('m_route_prompt', name=escape(p.name))}\n\n{loc['coords_hint']}"


def route_hint(lang: str) -> str:
    return locales.get(lang)["m_route_hint"]


def _warnings(loc: Locale, fc: MountainForecast, now: datetime) -> list[str]:
    hours = fc.upcoming(now)[: ROUTE_AHEAD + 1]
    if not hours:
        return []
    current, ahead = fc.summit(hours[0]), [fc.summit(h) for h in hours[1:]]
    warnings = []

    today = fc.day(now.date())
    sunset = today.get("sunset") if today else None
    if sunset and now < sunset and sunset - now < timedelta(hours=3):
        warnings.append(loc("w_dark", h=math.ceil((sunset - now).total_seconds() / 3600)))

    windy = max((c for c in ahead if c.wind is not None), key=lambda c: c.wind, default=None)
    if windy and windy.wind >= CAUTION_WIND and windy.wind - (current.wind or 0) >= 3:
        warnings.append(loc("w_wind", v=round(windy.wind), time=hm(windy.time)))
    storm = next((h for h in hours if fc.thunder(h)), None)
    if storm:
        warnings.append(loc("w_storm", time=hm(storm["time"])))
    if not current.phase:
        wet = next((c for c in ahead if c.phase), None)
        if wet:
            warnings.append(loc("w_precip", phase=_phase(loc, wet.phase).capitalize(), time=hm(wet.time)))
    if not current.in_cloud:
        cloudy = next((c for c in ahead if c.in_cloud), None)
        if cloudy:
            warnings.append(loc("w_cloud", time=hm(cloudy.time)))
    coldest = min((c.feels for c in [current, *ahead] if c.feels is not None), default=None)
    if coldest is not None and coldest <= COLD_WARNING:
        warnings.append(loc("w_cold", t=t(coldest)))
    return warnings


def route(lang: str, p: Peak, fc: MountainForecast, here: Here) -> str:
    loc = locales.get(lang)
    now = fc.local_now()
    row = fc.hour(now)
    summit = fc.summit(row)
    climb = p.ele - here.elevation

    lines = [loc("m_route_title", name=escape(p.name))]
    if climb > 50:
        km = distance_km(here.lat, here.lon, p.lat, p.lon)
        lines.append(loc("m_route_you", ele=round(here.elevation), km=loc.num(km, 1), climb=f"+{round(climb)}"))
    else:
        lines.append(loc("m_route_top", ele=round(here.elevation)))

    today = fc.day(now.date())
    if today and today.get("sunrise") and today.get("sunset"):
        if today["sunrise"] <= now < today["sunset"]:
            left = duration(loc, (today["sunset"] - now).total_seconds())
            lines.append(loc("m_route_sun", time=hm(now), set=hm(today["sunset"]), left=left))
        else:
            tomorrow = fc.day(now.date() + timedelta(days=1)) if now >= today["sunset"] else today
            rise = tomorrow.get("sunrise") if tomorrow else None
            lines.append(loc("m_route_dark", time=hm(now), rise=hm(rise) if rise else "—"))

    c = here.current
    icon, _ = weather(loc, c.get("weather_code"), c.get("is_day", 1))
    lines += [
        "",
        loc("m_here", icon=icon, t=t(c.get("temperature_2m")), feels=t(c.get("apparent_temperature")),
            v=loc.num(c.get("wind_speed_10m"))),
        loc("m_summit_short", t=t(summit.temp), feels=t(summit.feels), v=loc.num(summit.wind)),
    ]

    if climb > 50:
        bands = route_bands(here.elevation, p.ele)
        lines += ["", loc["m_way_up"], *_profile_rows(loc, fc, row, bands, you=bands[-1])]

    ahead = fc.upcoming(now)[1:ROUTE_AHEAD + 3:2]
    if ahead:
        cells = []
        for h in ahead:
            s = fc.summit(h)
            mark = PHASE_ICON[s.phase] if s.phase else ("🌫" if s.in_cloud else "")
            cells.append(f"{hm(s.time)} {t(s.temp)} 💨{loc.num(s.wind)}{(' ' + mark) if mark else ''}")
        lines += ["", loc["m_next_hours"], " · ".join(cells[:2]), " · ".join(cells[2:4])]

    warnings = _warnings(loc, fc, now)
    lines.append("")
    if warnings:
        lines += [loc["m_warnings"], *(f"• {w}" for w in warnings)]
    else:
        lines.append(loc["m_all_good"])
    lines += ["", _updated(loc, fc)]
    return "\n".join(lines)


# ── офлайн-копия ────────────────────────────────────────────────────────────

def offline(lang: str, p: Peak, fc: MountainForecast) -> str:
    """Самодостаточная сводка, которая остаётся в чате и читается без интернета."""
    loc = locales.get(lang)
    now = fc.local_now()
    today = now.date()
    row = fc.hour(now)
    lines = [
        loc("m_offline_header", name=escape(p.name), ele=p.ele, date=loc.date(now), time=hm(now)),
        "",
        *_summit_now(loc, fc, row),
        *_sun_and_uv(loc, fc),
        "",
        loc["m_way_up"],
        *_profile_rows(loc, fc, row, summit_bands(p.ele)),
        "",
        loc("m_hourly_title", name=escape(p.name), ele=p.ele),
    ]
    current_day = None
    for h in fc.upcoming(now)[:36:3]:
        if h["time"].date() != current_day:
            current_day = h["time"].date()
            lines.append(f"<b>{day_label(loc, current_day, today)}</b>")
        lines.append(_hour_row(loc, fc, h))
    lines += ["", loc["m_windows"], *(_day_line(loc, o, today) for o in fc.outlook()[:5])]
    return "\n".join(lines)
