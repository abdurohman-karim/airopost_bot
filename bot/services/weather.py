"""Клиент погодных API.

* Погода и прогноз — Open-Meteo (бесплатно, без ключа).
* Качество воздуха — Open-Meteo Air Quality (модель CAMS) + IQAir, если задан ключ.
  IQAir даёт индекс по реальным станциям мониторинга, Open-Meteo — концентрации
  всех загрязнителей и почасовой прогноз AQI.
* Поиск городов — Open-Meteo Geocoding, адрес по координатам — OpenStreetMap Nominatim.
"""
from __future__ import annotations

import asyncio
import logging
import time
from urllib.parse import urlencode

import aiohttp

from bot.services.models import AirQuality, Forecast, Place, Report, WeatherError, rows

log = logging.getLogger(__name__)

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
IQAIR_URL = "https://api.airvisual.com/v2/nearest_city"

USER_AGENT = "AiroPostBot/1.0 (Telegram weather bot)"

CURRENT = [
    "temperature_2m", "apparent_temperature", "relative_humidity_2m", "dew_point_2m",
    "is_day", "weather_code", "cloud_cover", "precipitation", "visibility", "uv_index",
    "pressure_msl", "surface_pressure",
    "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
]
HOURLY = [
    "temperature_2m", "apparent_temperature", "relative_humidity_2m", "is_day",
    "weather_code", "precipitation_probability", "precipitation",
    "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "uv_index",
]
DAILY = [
    "weather_code", "temperature_2m_max", "temperature_2m_min",
    "apparent_temperature_max", "apparent_temperature_min",
    "sunrise", "sunset", "daylight_duration", "uv_index_max",
    "precipitation_sum", "precipitation_probability_max",
    "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant",
]
POLLUTANTS = [
    "pm2_5", "pm10", "ozone", "nitrogen_dioxide", "sulphur_dioxide", "carbon_monoxide", "dust",
]
AIR_CURRENT = ["us_aqi", "european_aqi", *POLLUTANTS, *(f"us_aqi_{p}" for p in POLLUTANTS[:6])]

IQAIR_POLLUTANTS = {
    "p2": "pm2_5", "p1": "pm10", "o3": "ozone",
    "n2": "nitrogen_dioxide", "s2": "sulphur_dioxide", "co": "carbon_monoxide",
}

WEATHER_TTL = 10 * 60
AIR_TTL = 20 * 60
IQAIR_TTL = 30 * 60   # бесплатный тариф IQAir ограничен по числу запросов
FRESH_TTL = 60        # кнопка «Обновить» берёт данные не старше минуты
GEO_TTL = 24 * 60 * 60


class WeatherService:
    def __init__(self, iqair_key: str | None = None) -> None:
        self._iqair_key = iqair_key
        self._session: aiohttp.ClientSession | None = None
        self._cache: dict[str, tuple[float, dict]] = {}
        self._nominatim_lock = asyncio.Lock()
        self._nominatim_last = 0.0

    async def start(self) -> None:
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=15),
            headers={"User-Agent": USER_AGENT},
        )

    async def close(self) -> None:
        if self._session:
            await self._session.close()

    async def _get(self, url: str, params: dict[str, str], ttl: float) -> dict:
        key = f"{url}?{urlencode(sorted(params.items()))}"
        now = time.monotonic()
        cached = self._cache.get(key)
        if cached and now - cached[0] < ttl:
            return cached[1]
        assert self._session, "WeatherService.start() не вызван"
        try:
            async with self._session.get(url, params=params) as resp:
                if resp.status != 200:
                    raise WeatherError(f"{url}: HTTP {resp.status}")
                data = await resp.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as e:
            # В текст ошибки не кладём параметры — там может быть ключ IQAir
            raise WeatherError(f"{url}: {type(e).__name__}") from None
        self._cache[key] = (now, data)
        if len(self._cache) > 2000:
            self._cache = {k: v for k, v in self._cache.items() if now - v[0] < GEO_TTL}
        return data

    async def forecast(self, lat: float, lon: float, fresh: bool = False) -> Forecast:
        params = {
            "latitude": f"{lat:.2f}",
            "longitude": f"{lon:.2f}",
            "current": ",".join(CURRENT),
            "hourly": ",".join(HOURLY),
            "daily": ",".join(DAILY),
            "timezone": "auto",
            "forecast_days": "7",
            "wind_speed_unit": "ms",
        }
        data = await self._get(FORECAST_URL, params, FRESH_TTL if fresh else WEATHER_TTL)
        return Forecast.parse(data)

    async def air(self, lat: float, lon: float, fresh: bool = False) -> AirQuality | None:
        """Индекс качества воздуха. Возвращает None, если ни один источник не ответил."""
        open_meteo, iqair = await asyncio.gather(
            self._air_open_meteo(lat, lon, fresh),
            self._air_iqair(lat, lon),
            return_exceptions=True,
        )
        if isinstance(open_meteo, BaseException):
            log.warning("Open-Meteo Air Quality: %s", open_meteo)
            open_meteo = None
        if isinstance(iqair, BaseException):
            log.warning("IQAir: %s", iqair)
            iqair = None

        air = open_meteo
        if iqair:
            pollution = iqair["current"]["pollution"]
            if air is None:
                air = AirQuality(aqi=None, main_pollutant=None, source="IQAir")
            air.aqi = pollution.get("aqius")
            air.main_pollutant = IQAIR_POLLUTANTS.get(pollution.get("mainus"), air.main_pollutant)
            air.source = "IQAir"
            air.station = iqair.get("city")
        return air

    async def _air_open_meteo(self, lat: float, lon: float, fresh: bool) -> AirQuality:
        params = {
            "latitude": f"{lat:.2f}",
            "longitude": f"{lon:.2f}",
            "current": ",".join(AIR_CURRENT),
            "hourly": "us_aqi",
            "timezone": "auto",
            "forecast_days": "2",
        }
        data = await self._get(AIR_URL, params, FRESH_TTL if fresh else AIR_TTL)
        current = data.get("current") or {}
        sub_indexes = {
            p: current[f"us_aqi_{p}"]
            for p in POLLUTANTS
            if current.get(f"us_aqi_{p}") is not None
        }
        return AirQuality(
            aqi=current.get("us_aqi"),
            main_pollutant=max(sub_indexes, key=sub_indexes.get, default=None),
            source="Open-Meteo (CAMS)",
            eu_aqi=current.get("european_aqi"),
            pollutants={p: current.get(p) for p in POLLUTANTS},
            hourly=rows(data.get("hourly")),
            tz_name=data.get("timezone") or "UTC",
            utc_offset=data.get("utc_offset_seconds") or 0,
        )

    async def _air_iqair(self, lat: float, lon: float) -> dict | None:
        if not self._iqair_key:
            return None
        params = {"lat": f"{lat:.2f}", "lon": f"{lon:.2f}", "key": self._iqair_key}
        data = await self._get(IQAIR_URL, params, IQAIR_TTL)
        if data.get("status") != "success":
            raise WeatherError(f"IQAir: {data.get('data', {}).get('message', data.get('status'))}")
        return data["data"]

    async def report(self, lat: float, lon: float, fresh: bool = False) -> Report:
        forecast, air = await asyncio.gather(
            self.forecast(lat, lon, fresh), self.air(lat, lon, fresh), return_exceptions=True,
        )
        if isinstance(forecast, BaseException):
            raise forecast
        if isinstance(air, BaseException):
            log.warning("Air quality: %s", air)
            air = None
        return Report(forecast=forecast, air=air)

    async def search(self, query: str) -> list[Place]:
        """Поиск населённого пункта. «Ташкент, Узбекистан» — после запятой уточнение."""
        name, _, hint = query.partition(",")
        name = name.strip()
        if len(name) < 2:
            return []
        params = {"name": name, "count": "10", "language": "ru", "format": "json"}
        data = await self._get(GEOCODING_URL, params, GEO_TTL)
        places = [
            Place(
                name=r["name"],
                lat=r["latitude"],
                lon=r["longitude"],
                region=r.get("admin1"),
                country=r.get("country"),
            )
            for r in data.get("results") or []
        ]
        hint = hint.strip().lower()
        if hint:
            places = [p for p in places if hint in p.full.lower()] or places
        return places[:6]

    async def reverse(self, lat: float, lon: float) -> str | None:
        """Название места по координатам (Nominatim разрешает не больше 1 запроса в секунду)."""
        params = {
            "lat": f"{lat:.4f}",
            "lon": f"{lon:.4f}",
            "format": "jsonv2",
            "accept-language": "ru",
            "zoom": "14",
        }
        async with self._nominatim_lock:
            delay = 1.0 - (time.monotonic() - self._nominatim_last)
            if delay > 0:
                await asyncio.sleep(delay)
            try:
                data = await self._get(NOMINATIM_URL, params, GEO_TTL)
            except WeatherError as e:
                log.warning("Nominatim: %s", e)
                return None
            finally:
                self._nominatim_last = time.monotonic()

        address = data.get("address") or {}
        locality = next(
            (address[k] for k in ("city", "town", "village", "hamlet", "municipality", "county", "state")
             if address.get(k)),
            None,
        )
        district = address.get("suburb") or address.get("city_district") or address.get("district")
        parts = [district, locality] if district and locality else [locality, address.get("country")]
        title = ", ".join(dict.fromkeys(p for p in parts if p))
        return title or data.get("name") or None
