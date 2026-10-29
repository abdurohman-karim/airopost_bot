"""Расписание ежедневной сводки. Время рассылки — местное для выбранной местности."""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from bot.db import User
from bot.services.models import get_tz

# Если бот был выключен в момент рассылки, сводка догонит пользователя в течение этого окна
CATCH_UP = timedelta(minutes=60)

_TIME_RE = re.compile(r"^\s*([01]?\d|2[0-3])\s*[:.\-\s]?\s*([0-5]\d)\s*$")


def parse_time(text: str) -> str | None:
    """«7:30», «07.30», «0730» → «07:30». None, если это не время."""
    match = _TIME_RE.match(text)
    if not match:
        return None
    return f"{int(match[1]):02d}:{match[2]}"


def local_now(tz_name: str | None) -> datetime:
    return datetime.now(get_tz(tz_name))


def _target(now: datetime, hhmm: str) -> datetime:
    hour, minute = map(int, hhmm.split(":"))
    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)


def is_due(user: User) -> bool:
    now = local_now(user.tz)
    if user.last_sent == now.date().isoformat():
        return False
    target = _target(now, user.notify_time)
    return target <= now < target + CATCH_UP


def last_sent_after_change(tz_name: str | None, hhmm: str) -> str | None:
    """Значение last_sent после смены времени, местности или включения рассылки.

    Если выбранное время сегодня уже прошло — считаем сегодняшнюю сводку отправленной,
    чтобы она не пришла сразу же, а пришла завтра. Иначе — разрешаем отправку сегодня.
    """
    now = local_now(tz_name)
    return now.date().isoformat() if now >= _target(now, hhmm) else None


def next_send(user: User) -> datetime | None:
    if not (user.notify_enabled and user.has_location):
        return None
    now = local_now(user.tz)
    target = _target(now, user.notify_time)
    if user.last_sent != now.date().isoformat() and now < target + CATCH_UP:
        return target
    return target + timedelta(days=1)


# Время в базе (выходы, точка с маршрута) — UTC в формате SQLite: так его можно сравнивать прямо в SQL
DB_FORMAT = "%Y-%m-%d %H:%M:%S"


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def to_db(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime(DB_FORMAT)


def from_db(value: str) -> datetime:
    return datetime.strptime(value, DB_FORMAT).replace(tzinfo=timezone.utc)
