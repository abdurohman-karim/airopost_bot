"""«Куда на выходные»: оценка вершин на ближайшие субботу и воскресенье."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from bot.db import Peak
from bot.services import MountainService, WeatherError
from bot.services.mountain import DayOutlook

RANK = {"good": 0, "caution": 1, "bad": 2}
MAX_PEAKS = 30
PARALLEL = 6
LATE_HOUR = 15        # после 15:00 восхождение сегодня уже не начать — смотрим дальше
DEFAULT_TZ = "Asia/Tashkent"   # если у пользователя нет домашней местности — каталог в Узбекистане


@dataclass
class Entry:
    peak: Peak
    days: list[DayOutlook]

    @property
    def best(self) -> DayOutlook:
        return min(self.days, key=lambda o: (RANK[o.rating], len(o.reasons)))


def weekend_days(now: datetime) -> list[date]:
    """Дни ближайших выходных, когда ещё можно выйти на маршрут."""
    today, wd = now.date(), now.weekday()
    late = now.hour >= LATE_HOUR
    if wd == 5:
        return [today + timedelta(days=1)] if late else [today, today + timedelta(days=1)]
    if wd == 6 and not late:
        return [today]
    saturday = today + timedelta(days=(5 - wd) % 7 or 7)
    return [saturday, saturday + timedelta(days=1)]


def weekend_key(days: list[date]) -> str:
    """Суббота выходных — общий ключ для «уже отправили прогноз на эти выходные»."""
    first = days[0]
    return (first - timedelta(days=1) if first.weekday() == 6 else first).isoformat()


def rank(entry: Entry) -> tuple:
    ranks = [RANK[o.rating] for o in entry.days]
    return min(ranks), sum(ranks), max((o.wind_max or 0) for o in entry.days)


def unique(peaks: list[Peak]) -> list[Peak]:
    """Без дублей: опубликованная личная вершина есть и в каталоге."""
    seen, result = set(), []
    for peak in peaks:
        key = (round(peak.lat, 3), round(peak.lon, 3))
        if key not in seen:
            seen.add(key)
            result.append(peak)
    return result


async def collect(mountains: MountainService, peaks: list[Peak], days: list[date]) -> list[Entry]:
    semaphore = asyncio.Semaphore(PARALLEL)

    async def one(peak: Peak) -> Entry | None:
        async with semaphore:
            try:
                fc = await mountains.forecast(peak.lat, peak.lon, peak.ele)
            except WeatherError:
                return None
        outlooks = [o for o in fc.outlook() if o.day in days]
        return Entry(peak, outlooks) if outlooks else None

    entries = await asyncio.gather(*(one(p) for p in unique(peaks)[:MAX_PEAKS]))
    return sorted((e for e in entries if e), key=rank)
