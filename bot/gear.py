"""Что взять с собой: чек-лист снаряжения по прогнозу на вершине в выбранный день."""
from __future__ import annotations

from dataclasses import dataclass, field

from bot.services.mountain import DayOutlook, MountainForecast, summit_uv

# Номер вещи — бит в callback data отметок «собрано». Порядок не менять, новые — только в конец.
ITEMS = (
    "water", "food", "headlamp", "power", "firstaid", "glasses", "sunscreen", "cap", "beanie", "gloves",
    "fleece", "down", "mittens", "windproof", "rain", "drybag", "crampons", "poles", "gaiters", "axe", "thermos",
)

WINTER_MONTHS = {11, 12, 1, 2, 3, 4}
SNOWY_MM = 3              # столько снега (мм воды ≈ см) за 3 дня — на тропе снег
HOT_SUMMIT = 15           # на вершине тепло — внизу на тропе жара


@dataclass
class Item:
    key: str
    reason: str | None = None                       # ключ локали с пояснением
    params: dict = field(default_factory=dict)

    @property
    def bit(self) -> int:
        return 1 << ITEMS.index(self.key)


@dataclass
class Checklist:
    items: list[Item]
    notes: list[tuple[str, dict]]                   # советы без галочки: ключ локали и параметры
    snow_cm: int


def build(fc: MountainForecast, o: DayOutlook) -> Checklist:
    ele = fc.elevation
    feels = o.feels_min if o.feels_min is not None else o.t_min
    wind = o.wind_max or 0
    prob = o.prob_max or 0
    uv = summit_uv(o.uv_max, ele) if o.uv_max is not None else 0
    snow = fc.recent_snow()
    snowy = snow >= SNOWY_MM or o.phase in ("snow", "sleet")
    frost = o.fl_min is not None and o.fl_min < ele              # днём на вершине бывает ниже нуля
    winter = o.day.month in WINTER_MONTHS and ele >= 2000
    hot = o.t_max is not None and o.t_max >= HOT_SUMMIT

    day = fc.day(o.day) or {}
    sunset = day.get("sunset")
    items = [
        Item("water", "gr_water_hot" if hot else "gr_water"),
        Item("food"),
        Item("headlamp", "gr_headlamp", {"time": sunset.strftime("%H:%M")} if sunset else {"time": "—"}),
        Item("power", "gr_power"),
        Item("firstaid"),
        Item("poles", "gr_poles"),
    ]
    if feels is not None:
        for key, limit in (("fleece", 12), ("beanie", 5), ("gloves", 5), ("down", -5), ("mittens", -15),
                           ("thermos", 0)):
            if feels <= limit:
                items.append(Item(key, "gr_feels", {"t": round(feels)}))
    if wind >= 8:
        items.append(Item("windproof", "gr_wind", {"v": round(wind)}))
    if o.precip >= 0.5 or prob >= 40:
        items.append(Item("rain", "gr_precip" if o.precip >= 0.5 else "gr_prob",
                          {"mm": o.precip, "phase": o.phase, "p": prob}))
    if o.precip >= 2 or prob >= 60:
        items.append(Item("drybag"))
    if frost and (snowy or winter):
        reason = "gr_ice_snow" if snow >= SNOWY_MM else "gr_ice_winter"
        items.append(Item("crampons", reason, {"cm": round(snow)}))
        items.append(Item("gaiters", "gr_snow"))
        if ele >= 3500:
            items.append(Item("axe", "gr_axe"))
    if uv >= 3 or snowy:
        items.append(Item("glasses", "gr_glare" if snowy else "gr_uv", {"uv": round(uv)}))
    if uv >= 3:
        items.append(Item("sunscreen", "gr_uv", {"uv": round(uv)}))
    if uv >= 6 or hot:
        items.append(Item("cap", "gr_sun"))

    notes: list[tuple[str, dict]] = []
    if o.rating == "bad":
        notes.append(("gn_bad", {}))
    storm = next((params for key, params in o.reasons if key in ("r_thunder", "r_storm_risk")), None)
    if storm:
        notes.append(("gn_storm", storm))
    if o.best:
        notes.append(("gn_best", {"start": o.best[0], "end": o.best[1]}))
    if ele >= 3000:
        notes.append(("gn_altitude", {}))
    if fc.snow().level >= 2:
        notes.append(("gn_avalanche", {}))
    return Checklist(items=items, notes=notes, snow_cm=round(snow))
