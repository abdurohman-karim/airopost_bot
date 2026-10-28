from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class WeatherError(Exception):
    """Внешний API недоступен или вернул ошибку."""


def get_tz(name: str | None, offset_seconds: int | None = None) -> tzinfo:
    if name:
        try:
            return ZoneInfo(name)
        except (ZoneInfoNotFoundError, ValueError):
            pass
    if offset_seconds is not None:
        return timezone(timedelta(seconds=offset_seconds))
    return timezone.utc


def _parse_time(value: str) -> datetime | date:
    return datetime.fromisoformat(value) if "T" in value else date.fromisoformat(value)


def rows(block: dict | None) -> list[dict]:
    """Open-Meteo отдаёт параллельные массивы — превращаем их в список словарей по времени."""
    if not block or "time" not in block:
        return []
    keys = [k for k in block if k != "time"]
    return [
        {"time": _parse_time(t), **{k: block[k][i] for k in keys}}
        for i, t in enumerate(block["time"])
    ]


@dataclass
class Forecast:
    tz_name: str
    utc_offset: int
    current: dict
    hourly: list[dict]
    daily: list[dict]

    @classmethod
    def parse(cls, data: dict) -> Forecast:
        current = dict(data.get("current") or {})
        if "time" in current:
            current["time"] = _parse_time(current["time"])
        daily = rows(data.get("daily"))
        for day in daily:
            for key in ("sunrise", "sunset"):
                day[key] = _parse_time(day[key]) if day.get(key) else None
        return cls(
            tz_name=data.get("timezone") or "UTC",
            utc_offset=data.get("utc_offset_seconds") or 0,
            current=current,
            hourly=rows(data.get("hourly")),
            daily=daily,
        )

    @property
    def tz(self) -> tzinfo:
        return get_tz(self.tz_name, self.utc_offset)

    def local_now(self) -> datetime:
        """Текущее местное время в точке прогноза (без tzinfo, как и время в ответах API)."""
        return datetime.now(self.tz).replace(tzinfo=None)

    def upcoming_hours(self, start: datetime | None = None) -> list[dict]:
        start = (start or self.local_now()).replace(minute=0, second=0, microsecond=0)
        return [h for h in self.hourly if h["time"] > start]


@dataclass
class AirQuality:
    aqi: int | None                      # US AQI — та же шкала, что у IQAir
    main_pollutant: str | None           # ключ: pm2_5, pm10, ozone, ...
    source: str
    station: str | None = None
    eu_aqi: int | None = None
    pollutants: dict[str, float | None] = field(default_factory=dict)
    hourly: list[dict] = field(default_factory=list)
    tz_name: str = "UTC"
    utc_offset: int = 0

    def local_now(self) -> datetime:
        return datetime.now(get_tz(self.tz_name, self.utc_offset)).replace(tzinfo=None)


@dataclass
class Report:
    forecast: Forecast
    air: AirQuality | None


@dataclass
class Place:
    name: str
    lat: float
    lon: float
    region: str | None = None
    country: str | None = None

    @property
    def short(self) -> str:
        return ", ".join(_unique([self.name, self.country]))

    @property
    def full(self) -> str:
        return ", ".join(_unique([self.name, self.region, self.country]))

    def to_dict(self) -> dict:
        return asdict(self)


def _unique(parts: list[str | None]) -> list[str]:
    result: list[str] = []
    for part in parts:
        if part and part not in result:
            result.append(part)
    return result
