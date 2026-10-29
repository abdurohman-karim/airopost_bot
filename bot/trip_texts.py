"""Тексты контрольного срока: выход на маршрут, напоминание, тревога доверенным контактам."""
from __future__ import annotations

from datetime import datetime, timedelta
from html import escape

from bot import locales, timeutil
from bot.db import Peak, Trip, User
from bot.links import map_url
from bot.locales import Locale
from bot.services.models import get_tz
from bot.texts import duration, hm

DEADLINE_HOURS = (3, 4, 6, 8, 10, 12)


def local(dt: datetime, tz: str) -> datetime:
    return dt.astimezone(get_tz(tz))


def deadline_options(now: datetime, tz: str) -> list[tuple[int, str]]:
    """Кнопки срока: (часов, «+4 ч · 18:40»)."""
    return [(h, f"+{h} · {hm(local(now + timedelta(hours=h), tz))}") for h in DEADLINE_HOURS]


def _names(contacts: list[tuple[int, str]]) -> str:
    return ", ".join(escape(name) for _, name in contacts)


def _contacts_line(loc: Locale, contacts: list[tuple[int, str]]) -> str:
    return loc("trip_contacts", names=_names(contacts)) if contacts else loc["trip_no_contacts"]


def _left(loc: Locale, span: timedelta) -> str:
    return duration(loc, max(span.total_seconds(), 0))


def _ago(loc: Locale, span: timedelta) -> str:
    minutes = int(span.total_seconds() // 60)
    if minutes < 2:
        return loc["sos_now"]
    return loc("sos_min_ago", n=minutes) if minutes < 60 else loc("sos_h_ago", h=minutes // 60, m=minutes % 60)


def when(loc: Locale, value: str, tz: str) -> str:
    """Время срока; если он не сегодня по местному времени — с датой."""
    dt, today = local(timeutil.from_db(value), tz), local(timeutil.utc_now(), tz).date()
    return hm(dt) if dt.date() == today else f"{loc.day_month(dt.date())}, {hm(dt)}"


def _point(loc: Locale, user: User, tz: str) -> list[str]:
    """Последняя точка с маршрута — в тревожном сообщении и на экране выхода."""
    if user.route_lat is None or user.route_lon is None or not user.route_at:
        return [loc["trip_no_point"]]
    at = timeutil.from_db(user.route_at)
    ago = _ago(loc, timeutil.utc_now() - at)
    lines = [loc("trip_point", time=hm(local(at, tz)), ago=ago), f"<code>{user.route_lat:.5f}, {user.route_lon:.5f}</code>"]
    if user.route_ele is not None:
        lines[-1] += loc("trip_point_ele", ele=round(user.route_ele))
    lines.append(loc("sos_map", url=map_url(user.route_lat, user.route_lon)))
    return lines


def setup(
    lang: str, peak: Peak, contacts: list[tuple[int, str]], sunset: datetime | None, error: bool = False,
) -> str:
    loc = locales.get(lang)
    lines = [loc["time_error"]] if error else []
    lines += [loc("trip_title", name=escape(peak.name)), "", loc["trip_intro"], "", _contacts_line(loc, contacts)]
    if sunset:
        lines.append(loc("trip_sunset", time=hm(sunset)))
    lines += ["", loc["trip_pick"]]
    return "\n".join(lines)


def active(lang: str, trip: Trip, user: User, contacts: list[tuple[int, str]], header: str | None = None) -> str:
    loc = locales.get(lang)
    now, deadline = timeutil.utc_now(), timeutil.from_db(trip.deadline)
    lines = [header, ""] if header else []
    lines += [
        loc("trip_active_title", name=escape(trip.peak_name)),
        loc("trip_started", time=hm(local(timeutil.from_db(trip.started_at), trip.tz))),
    ]
    if deadline > now:
        lines.append(loc("trip_deadline", time=when(loc, trip.deadline, trip.tz), left=_left(loc, deadline - now)))
    else:
        lines.append(loc("trip_overdue", time=when(loc, trip.deadline, trip.tz), late=_left(loc, now - deadline)))
    lines += ["", *_point(loc, user, trip.tz), "", _contacts_line(loc, contacts)]
    if trip.alerted:
        lines.append(loc["trip_alerted_note"])
    lines += ["", loc["trip_live_hint"]]
    return "\n".join(lines)


def reminder(lang: str, trip: Trip) -> str:
    loc = locales.get(lang)
    return loc("trip_reminder", name=escape(trip.peak_name), time=when(loc, trip.deadline, trip.tz))


def alarm(lang: str, trip: Trip, owner: User) -> str:
    """Тревога доверенному контакту: человек не отметился к сроку."""
    loc = locales.get(lang)
    who = f'<a href="tg://user?id={trip.user_id}">{escape(trip.user_name)}</a>'
    lines = [
        loc("trip_alarm_title", who=escape(trip.user_name)),
        "",
        loc(
            "trip_alarm_body", who=who, name=escape(trip.peak_name), ele=trip.peak_ele,
            start=hm(local(timeutil.from_db(trip.started_at), trip.tz)),
            deadline=when(loc, trip.deadline, trip.tz),
            date=loc.date(local(timeutil.from_db(trip.started_at), trip.tz)),
        ),
        "",
        *_point(loc, owner, trip.tz),
        "",
        loc("trip_alarm_todo", who=who),
    ]
    return "\n".join(lines)


def owner_alerted(lang: str, trip: Trip, contacts: list[tuple[int, str]]) -> str:
    return locales.get(lang)("trip_owner_alerted", names=_names(contacts) or "—")


def back_notice(lang: str, trip: Trip) -> str:
    return locales.get(lang)("trip_back_notice", who=escape(trip.user_name), name=escape(trip.peak_name))


def extended_notice(lang: str, trip: Trip) -> str:
    loc = locales.get(lang)
    return loc("trip_extended_notice", who=escape(trip.user_name), time=when(loc, trip.deadline, trip.tz))


def contacts_screen(lang: str, contacts: list[tuple[int, str]]) -> str:
    loc = locales.get(lang)
    lines = [loc["contacts_title"], "", loc["contacts_intro"], ""]
    lines.append(loc("contacts_list", names=_names(contacts)) if contacts else loc["contacts_empty"])
    return "\n".join(lines)


def invite(lang: str, owner_name: str) -> str:
    return locales.get(lang)("invite_text", who=escape(owner_name))


def invite_share(lang: str) -> str:
    return locales.get(lang)["invite_share"]
