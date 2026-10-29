"""Горная погода: условия на вершине, профиль высот, окна для восхождения, точка на маршруте.

Температура, ветер и влажность на высоте берутся из «свободной атмосферы» — по уровням
давления модели (1000…300 гПа) с интерполяцией по геопотенциальной высоте. Так считают
горные прогнозы: у приземной температуры модели рельеф сглажен, и для вершины она
получается заметно теплее реальной. Для точки, где стоит человек, — обычная приземная погода.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from bot.services.models import WeatherError, get_tz, rows
from bot.services.weather import FORECAST_URL, FRESH_TTL, GEO_TTL, WEATHER_TTL, WeatherService

ELEVATION_URL = "https://api.open-meteo.com/v1/elevation"
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"

LEVELS = [1000, 925, 850, 800, 700, 600, 500, 400, 300]
LEVEL_VARS = ["temperature", "geopotential_height", "wind_speed", "wind_direction", "relative_humidity"]

SUMMIT_HOURLY = [
    "precipitation", "precipitation_probability", "weather_code", "cloud_cover",
    "wind_gusts_10m", "freezing_level_height", "cape", "uv_index", "is_day",
    *(f"{var}_{level}hPa" for level in LEVELS for var in LEVEL_VARS),
]
SUMMIT_DAILY = ["sunrise", "sunset", "daylight_duration", "uv_index_max"]
HERE_CURRENT = [
    "temperature_2m", "apparent_temperature", "weather_code", "is_day", "precipitation",
    "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m", "relative_humidity_2m",
]

PEAK_TYPES = {"peak", "volcano", "saddle", "ridge", "hill", "mountain_range", "rock", "cliff", "glacier"}

LAPSE_RATE = 6.5 / 1000   # °C на метр — для экстраполяции ниже самого нижнего уровня
IN_CLOUD_RH = 95          # при такой влажности на высоте вершина в облаке/тумане
UV_PER_KM = 0.08          # УФ растёт примерно на 8 % на каждый километр высоты
PAST_DAYS = 3             # прошедшие дни в прогнозе — чтобы знать, сколько недавно выпало снега

# Пороги оценки дня для восхождения (дневные часы на вершине)
DAY_HOURS = range(6, 19)
BAD_WIND, CAUTION_WIND = 20, 12           # м/с
BAD_PRECIP, CAUTION_PRECIP = 5.0, 1.0     # мм за день
CAUTION_PROB = 50                         # %
CAUTION_FEELS = -25                       # °C, ощущаемая
STORM_CAPE, CAUTION_CAPE = 1000, 500      # Дж/кг
CAUTION_CLOUD_HOURS = 6
BEST_MIN_HOURS = 2                        # короче — не окно, а случайный час

# Время в пути по горной тропе (правило Нейсмита, поправленное на горные тропы с рюкзаком)
TRAIL_FACTOR = 1.3                        # тропа длиннее прямой на карте
UP_KMH, UP_MH = 4.0, 400                  # подъём: км/ч по горизонтали + метров набора в час
DOWN_KMH, DOWN_MH = 5.0, 800              # спуск


def summit_uv(uv: float, ele: float) -> float:
    """УФ-индекс модели с поправкой на высоту."""
    return uv * (1 + UV_PER_KM * ele / 1000)


def wind_chill(temp: float, wind_ms: float) -> float:
    """Ощущаемая температура на ветру (формула Environment Canada / NWS)."""
    v = wind_ms * 3.6
    if temp > 10 or v <= 4.8:
        return temp
    return 13.12 + 0.6215 * temp - 11.37 * v ** 0.16 + 0.3965 * temp * v ** 0.16


def precip_phase(temp: float, precip: float | None) -> str | None:
    if not precip or precip < 0.1:
        return None
    if temp <= 0.5:
        return "snow"
    if temp <= 2:
        return "sleet"
    return "rain"


# Код погоды модели описывает поверхность ячейки сетки, а не вершину — согласуем его с высотой
_RAIN_TO_SNOW = {51: 71, 53: 71, 55: 73, 56: 71, 57: 73, 61: 71, 63: 73, 65: 75, 66: 73, 67: 75,
                 80: 85, 81: 85, 82: 86}
_SNOW_TO_RAIN = {71: 61, 73: 63, 75: 65, 77: 61, 85: 80, 86: 81}


def summit_code(code: int | None, cloud_cover: float | None, in_cloud: bool, phase: str | None) -> int | None:
    if code is None or code >= 95:
        return code
    if phase in ("snow", "sleet"):
        return _RAIN_TO_SNOW.get(code, code if code >= 71 else 71)
    if phase == "rain":
        return _SNOW_TO_RAIN.get(code, code if 51 <= code < 71 or 80 <= code <= 82 else 61)
    if phase is None and code >= 51:          # модель даёт осадки, но на этой высоте их нет
        code = 3
    if in_cloud:
        return 45
    if code in (45, 48):                      # туман внизу, а вершина над ним
        cover = cloud_cover or 0
        return 3 if cover >= 70 else 2 if cover >= 30 else 1
    return code


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def summit_bands(summit: float, count: int = 5) -> list[int]:
    """Вершина и круглые высоты ниже неё: 3309 → 3309, 3000, 2500, 2000, 1500, 1000."""
    step = 500 if summit >= 2000 else 250
    top = math.floor((summit - step / 2) / step) * step
    bands = [round(summit)] + [top - i * step for i in range(count)]
    return [b for b in bands if b > 0]


def route_bands(low: float, high: float, count: int = 4) -> list[int]:
    """Высоты между точкой на маршруте и вершиной, сверху вниз, с шагом не меньше 100 м."""
    if high - low < 200:
        return [round(high), round(low)]
    inner = min(count, int((high - low) // 100) - 1)
    step = (high - low) / (inner + 1)
    middle = [round((high - step * i) / 50) * 50 for i in range(1, inner + 1)]
    return [round(high), *middle, round(low)]


def hike_hours(km: float, climb: float) -> tuple[float, float]:
    """Ориентировочное время подъёма и спуска в часах, без привалов: (вверх, вниз)."""
    trail, climb = km * TRAIL_FACTOR, max(climb, 0)
    return trail / UP_KMH + climb / UP_MH, trail / DOWN_KMH + climb / DOWN_MH


@dataclass
class RoutePlan:
    """Расчёт времени от точки на маршруте до вершины и обратно в эту точку."""
    up: timedelta
    down: timedelta
    summit_at: datetime                 # на вершине, если идти сейчас
    back_at: datetime                   # обратно в этой точке
    latest_summit: datetime | None      # позже — спуск уже после заката
    turnaround: datetime | None         # не успеть до заката: когда разворачиваться, где бы вы ни были


def route_plan(now: datetime, km: float, climb: float, sunset: datetime | None) -> RoutePlan:
    up_h, down_h = hike_hours(km, climb)
    up, down = timedelta(hours=up_h), timedelta(hours=down_h)
    plan = RoutePlan(up=up, down=down, summit_at=now + up, back_at=now + up + down, latest_summit=None, turnaround=None)
    if sunset and sunset > now:
        plan.latest_summit = sunset - down
        if plan.back_at > sunset:
            # Через τ часов пути спуск займёт down·τ/up — разворачиваться, пока τ·(1 + down/up) ≤ до заката
            plan.turnaround = now + (sunset - now) / (1 + down_h / up_h)
    return plan


@dataclass
class Conditions:
    """Условия на заданной высоте в конкретный час."""
    time: datetime
    elevation: float
    temp: float | None
    feels: float | None
    wind: float | None
    wind_dir: float | None
    in_cloud: bool
    precip: float
    precip_prob: int | None
    phase: str | None
    weather_code: int | None
    is_day: bool


@dataclass
class DayOutlook:
    day: date
    rating: str                       # good | caution | bad
    reasons: list[tuple[str, dict]]   # ключ локали и параметры
    t_min: float | None
    t_max: float | None
    feels_min: float | None
    wind_max: float | None
    precip: float
    prob_max: int | None
    phase: str | None
    fl_min: float | None
    fl_max: float | None
    thunder: bool
    best: tuple[datetime, datetime] | None = None   # самые спокойные часы на вершине: [начало, конец)
    uv_max: float | None = None


@dataclass
class MountainForecast:
    elevation: float
    tz_name: str
    utc_offset: int
    hourly: list[dict]
    daily: list[dict]

    def local_now(self) -> datetime:
        return datetime.now(get_tz(self.tz_name, self.utc_offset)).replace(tzinfo=None)

    def hour(self, at: datetime | None = None) -> dict:
        at = (at or self.local_now()).replace(minute=0, second=0, microsecond=0)
        return next((h for h in self.hourly if h["time"] >= at), self.hourly[-1])

    def upcoming(self, start: datetime | None = None) -> list[dict]:
        start = (start or self.local_now()).replace(minute=0, second=0, microsecond=0)
        return [h for h in self.hourly if h["time"] >= start]

    def day(self, d: date) -> dict | None:
        return next((x for x in self.daily if x["time"] == d), None)

    @staticmethod
    def _levels(row: dict, var: str) -> list[tuple[float, float]]:
        points = []
        for level in LEVELS:
            height, value = row.get(f"geopotential_height_{level}hPa"), row.get(f"{var}_{level}hPa")
            if height is not None and value is not None:
                points.append((height, value))
        return sorted(points)

    @classmethod
    def _interp(cls, row: dict, var: str, z: float) -> float | None:
        points = cls._levels(row, var)
        if not points:
            return None
        if z <= points[0][0]:
            low_h, low_v = points[0]
            return low_v + (low_h - z) * LAPSE_RATE if var == "temperature" else low_v
        if z >= points[-1][0]:
            return points[-1][1]
        for (h1, v1), (h2, v2) in zip(points, points[1:]):
            if h1 <= z <= h2:
                if var == "wind_direction":   # направление не усредняем — берём ближайший уровень
                    return v1 if z - h1 < h2 - z else v2
                return v1 + (v2 - v1) * (z - h1) / (h2 - h1)
        return None

    def at(self, row: dict, z: float) -> Conditions:
        temp = self._interp(row, "temperature", z)
        wind = self._interp(row, "wind_speed", z)
        rh = self._interp(row, "relative_humidity", z)
        precip = row.get("precipitation") or 0
        in_cloud = rh is not None and rh >= IN_CLOUD_RH
        phase = precip_phase(temp, precip) if temp is not None else None
        return Conditions(
            time=row["time"],
            elevation=z,
            temp=temp,
            feels=wind_chill(temp, wind) if temp is not None and wind is not None else temp,
            wind=wind,
            wind_dir=self._interp(row, "wind_direction", z),
            in_cloud=in_cloud,
            precip=precip,
            precip_prob=row.get("precipitation_probability"),
            phase=phase,
            weather_code=summit_code(row.get("weather_code"), row.get("cloud_cover"), in_cloud, phase),
            is_day=bool(row.get("is_day", 1)),
        )

    def summit(self, row: dict) -> Conditions:
        return self.at(row, self.elevation)

    def recent_snow(self, hours: int = PAST_DAYS * 24) -> float:
        """Снег и мокрый снег на вершине за последние часы, мм воды (≈ см свежего снега)."""
        now = self.local_now()
        start = now - timedelta(hours=hours)
        return sum(
            c.precip for c in (self.summit(h) for h in self.hourly if start <= h["time"] < now)
            if c.phase in ("snow", "sleet")
        )

    @staticmethod
    def thunder(row: dict) -> bool:
        return (row.get("weather_code") or 0) >= 95 or (
            (row.get("cape") or 0) >= STORM_CAPE and (row.get("precipitation") or 0) > 0
        )

    def outlook(self) -> list[DayOutlook]:
        result = []
        now = self.local_now().replace(minute=0, second=0, microsecond=0)
        for d in sorted({h["time"].date() for h in self.hourly if h["time"].date() >= now.date()}):
            # Для сегодняшнего дня учитываем только оставшиеся светлые часы
            hours = [
                h for h in self.hourly
                if h["time"].date() == d and h["time"].hour in DAY_HOURS and h["time"] >= now
            ]
            if not hours:
                continue
            cond = [self.summit(h) for h in hours]
            temps = [c.temp for c in cond if c.temp is not None]
            feels = [c.feels for c in cond if c.feels is not None]
            winds = [c.wind for c in cond if c.wind is not None]
            probs = [c.precip_prob for c in cond if c.precip_prob is not None]
            fls = [h["freezing_level_height"] for h in hours if h.get("freezing_level_height") is not None]
            capes = [h.get("cape") or 0 for h in hours]
            precip = sum(c.precip for c in cond)
            phases = [c.phase for c in cond if c.phase]
            phase = "snow" if "snow" in phases else "sleet" if "sleet" in phases else phases[0] if phases else None
            thunder = any(self.thunder(h) for h in hours)
            cloud_hours = sum(c.in_cloud for c in cond)
            wind_max = max(winds, default=None)
            feels_min = min(feels, default=None)

            bad, caution = [], []
            if thunder:
                first = next(h for h in hours if self.thunder(h))
                bad.append(("r_thunder", {"time": first["time"].strftime("%H:%M")}))
            elif max(capes, default=0) >= CAUTION_CAPE:
                first = next(h for h in hours if (h.get("cape") or 0) >= CAUTION_CAPE)
                caution.append(("r_storm_risk", {"time": first["time"].strftime("%H:%M")}))
            if wind_max is not None and wind_max >= BAD_WIND:
                bad.append(("r_wind", {"v": round(wind_max)}))
            elif wind_max is not None and wind_max >= CAUTION_WIND:
                caution.append(("r_wind", {"v": round(wind_max)}))
            if precip >= BAD_PRECIP:
                bad.append(("r_precip", {"mm": precip, "phase": phase}))
            elif precip >= CAUTION_PRECIP:
                caution.append(("r_precip", {"mm": precip, "phase": phase}))
            elif probs and max(probs) >= CAUTION_PROB:
                caution.append(("r_prob", {"p": max(probs)}))
            if feels_min is not None and feels_min <= CAUTION_FEELS:
                caution.append(("r_cold", {"t": round(feels_min)}))
            if cloud_hours >= CAUTION_CLOUD_HOURS:
                caution.append(("r_cloud", {"h": cloud_hours}))

            result.append(DayOutlook(
                day=d,
                rating="bad" if bad else "caution" if caution else "good",
                reasons=bad + caution,
                t_min=min(temps, default=None),
                t_max=max(temps, default=None),
                feels_min=feels_min,
                wind_max=wind_max,
                precip=precip,
                prob_max=max(probs, default=None),
                phase=phase,
                fl_min=min(fls, default=None),
                fl_max=max(fls, default=None),
                thunder=thunder,
                best=self._best_hours(hours, cond),
                uv_max=(self.day(d) or {}).get("uv_index_max"),
            ))
        return result

    def _best_hours(self, hours: list[dict], cond: list[Conditions]) -> tuple[datetime, datetime] | None:
        """Самый длинный отрезок спокойных часов: без грозы, осадков, облака и сильного ветра."""
        best, start = None, None
        for i, (h, c) in enumerate(zip(hours, cond)):
            calm = (
                not self.thunder(h) and (h.get("cape") or 0) < CAUTION_CAPE and not c.phase
                and not c.in_cloud and c.wind is not None and c.wind < CAUTION_WIND
            )
            # Отрезок рвётся и на плохом часе, и на пропуске в данных
            if calm and start is not None and h["time"] - hours[i - 1]["time"] != timedelta(hours=1):
                start = None
            if calm:
                start = i if start is None else start
                if best is None or i - start > best[1] - best[0]:
                    best = (start, i)
            else:
                start = None
        # Спокоен весь день — подсказывать нечего; короткий просвет — не окно
        if best is None or best[1] - best[0] + 1 < BEST_MIN_HOURS or best[1] - best[0] + 1 == len(hours):
            return None
        return hours[best[0]]["time"], hours[best[1]]["time"] + timedelta(hours=1)


@dataclass
class Here:
    """Приземная погода в точке, где стоит человек."""
    lat: float
    lon: float
    elevation: float
    current: dict


@dataclass
class PeakResult:
    name: str
    lat: float
    lon: float
    ele: float | None
    country: str | None = None

    def to_dict(self) -> dict:
        return {"name": self.name, "lat": self.lat, "lon": self.lon, "ele": self.ele, "country": self.country}


def _parse_ele(value: str | None) -> float | None:
    match = re.search(r"\d+(?:[.,]\d+)?", value or "")
    return float(match[0].replace(",", ".")) if match else None


class MountainService:
    def __init__(self, http: WeatherService) -> None:
        self._http = http

    async def forecast(self, lat: float, lon: float, ele: float, fresh: bool = False) -> MountainForecast:
        params = {
            "latitude": f"{lat:.4f}",
            "longitude": f"{lon:.4f}",
            "elevation": f"{ele:.0f}",
            "hourly": ",".join(SUMMIT_HOURLY),
            "daily": ",".join(SUMMIT_DAILY),
            "timezone": "auto",
            "forecast_days": "7",
            "past_days": str(PAST_DAYS),
            "wind_speed_unit": "ms",
        }
        data = await self._http.get_json(FORECAST_URL, params, FRESH_TTL if fresh else WEATHER_TTL)
        if not data.get("hourly"):
            raise WeatherError("mountain forecast: empty response")
        daily = rows(data.get("daily"))
        for day in daily:
            for key in ("sunrise", "sunset"):
                day[key] = datetime.fromisoformat(day[key]) if day.get(key) else None
        return MountainForecast(
            elevation=ele,
            tz_name=data.get("timezone") or "UTC",
            utc_offset=data.get("utc_offset_seconds") or 0,
            hourly=rows(data["hourly"]),
            daily=daily,
        )

    async def here(self, lat: float, lon: float, fresh: bool = False) -> Here:
        """Погода в точке. Высота — по цифровой модели рельефа в точных координатах."""
        params = {
            "latitude": f"{lat:.4f}",
            "longitude": f"{lon:.4f}",
            "current": ",".join(HERE_CURRENT),
            "timezone": "auto",
            "wind_speed_unit": "ms",
        }
        data = await self._http.get_json(FORECAST_URL, params, FRESH_TTL if fresh else WEATHER_TTL)
        return Here(lat=lat, lon=lon, elevation=data.get("elevation") or 0, current=data.get("current") or {})

    async def elevations(self, points: list[tuple[float, float]]) -> list[float | None]:
        if not points:
            return []
        params = {
            "latitude": ",".join(f"{lat:.4f}" for lat, _ in points),
            "longitude": ",".join(f"{lon:.4f}" for _, lon in points),
        }
        data = await self._http.get_json(ELEVATION_URL, params, GEO_TTL)
        values = data.get("elevation") or []
        return [values[i] if i < len(values) else None for i in range(len(points))]

    async def search(self, query: str, lang: str) -> list[PeakResult]:
        """Вершины и перевалы по названию из OpenStreetMap — там у них указана высота."""
        query = query.strip()
        if len(query) < 2:
            return []
        params = {
            "q": query,
            "format": "jsonv2",
            "extratags": "1",
            "limit": "20",
            "accept-language": f"{lang},en",
        }
        data = await self._http.nominatim(NOMINATIM_SEARCH_URL, params)
        results = _peaks_from_nominatim(data)[:6]

        missing = [r for r in results if r.ele is None]
        if missing:
            try:
                for r, ele in zip(missing, await self.elevations([(r.lat, r.lon) for r in missing])):
                    r.ele = ele
            except WeatherError:
                pass
        return results

    async def nearest_peak(self, lat: float, lon: float, lang: str, radius_km: float = 0.7) -> PeakResult | None:
        """Ближайшая вершина из OpenStreetMap к метке на карте: точные название и высота."""
        d_lat = radius_km / 111
        d_lon = d_lat / max(math.cos(math.radians(lat)), 0.1)
        params = {
            "q": "peak",
            "format": "jsonv2",
            "extratags": "1",
            "limit": "10",
            "bounded": "1",
            "viewbox": f"{lon - d_lon:.5f},{lat + d_lat:.5f},{lon + d_lon:.5f},{lat - d_lat:.5f}",
            "accept-language": f"{lang},en",
        }
        data = await self._http.nominatim(NOMINATIM_SEARCH_URL, params)
        peaks = [p for p in _peaks_from_nominatim(data) if p.ele]
        return min(peaks, key=lambda p: distance_km(lat, lon, p.lat, p.lon), default=None)


def _peaks_from_nominatim(data: dict | list) -> list[PeakResult]:
    results: list[PeakResult] = []
    seen = set()
    for item in data if isinstance(data, list) else []:
        if not (
            (item.get("category") == "natural" and item.get("type") in PEAK_TYPES)
            or item.get("category") == "mountain_pass"
            or item.get("type") == "mountain_pass"
        ):
            continue
        lat, lon = float(item["lat"]), float(item["lon"])
        key = (item.get("name"), round(lat, 2), round(lon, 2))
        if key in seen or not item.get("name"):
            continue
        seen.add(key)
        results.append(PeakResult(
            name=item["name"],
            lat=lat,
            lon=lon,
            ele=_parse_ele((item.get("extratags") or {}).get("ele")),
            country=(item.get("display_name") or "").split(",")[-1].strip() or None,
        ))
    return results
