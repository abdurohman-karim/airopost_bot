"""GPX-трек: разбор файла, длина, набор и сброс высоты, время в пути и точки для прогноза по пути."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta

from bot.services.mountain import DOWN_MH, UP_KMH, UP_MH, distance_km

MAX_POINTS = 400          # больше для расчёта не нужно — трек прореживаем
MAX_FILE = 5 * 1024 * 1024
ELE_NOISE = 5             # м: меньшие колебания высоты GPS не считаем набором
SMOOTH = 5                # точек в скользящем среднем высоты
CHECKPOINT_HOURS = 1      # прогноз примерно через каждый час пути
MAX_CHECKPOINTS = 12

Point = tuple[float, float, float | None]


class GpxError(ValueError):
    pass


def _tag(el: ET.Element) -> str:
    return el.tag.rsplit("}", 1)[-1]


def parse(data: bytes, fallback_name: str) -> tuple[str, list[Point]]:
    """Название и точки трека: trkpt, если их нет — rtept, иначе wpt."""
    if len(data) > MAX_FILE:
        raise GpxError("too big")
    if b"<!DOCTYPE" in data[:2048] or b"<!ENTITY" in data:
        raise GpxError("entities")     # GPX не использует сущности — такие файлы не разбираем
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        raise GpxError("xml") from e
    if _tag(root) != "gpx":
        raise GpxError("not gpx")

    name = None
    for el in root.iter():
        if _tag(el) == "name" and el.text and el.text.strip():
            name = el.text.strip()
            break
    for kind in ("trkpt", "rtept", "wpt"):
        points: list[Point] = []
        for el in root.iter():
            if _tag(el) != kind:
                continue
            try:
                lat, lon = float(el.get("lat")), float(el.get("lon"))
            except (TypeError, ValueError):
                continue
            ele = next((child.text for child in el if _tag(child) == "ele"), None)
            try:
                points.append((lat, lon, float(ele) if ele else None))
            except ValueError:
                points.append((lat, lon, None))
        if len(points) >= 2:
            return (name or fallback_name)[:64], thin(points)
    raise GpxError("no points")


def thin(points: list[Point], limit: int = MAX_POINTS) -> list[Point]:
    if len(points) <= limit:
        return points
    step = (len(points) - 1) / (limit - 1)
    return [points[round(i * step)] for i in range(limit)]


@dataclass
class Leg:
    """Точка трека с накопленными расстоянием, набором и временем пути от старта."""
    lat: float
    lon: float
    ele: float
    km: float
    hours: float


@dataclass
class Track:
    name: str
    legs: list[Leg]
    gain: float
    loss: float

    @property
    def km(self) -> float:
        return self.legs[-1].km

    @property
    def hours(self) -> float:
        return self.legs[-1].hours

    @property
    def top(self) -> Leg:
        return max(self.legs, key=lambda leg: leg.ele)

    @property
    def low(self) -> Leg:
        return min(self.legs, key=lambda leg: leg.ele)

    def checkpoints(self) -> list[Leg]:
        """Старт, примерно каждый час пути, высшая точка и финиш."""
        picked, next_hour = [self.legs[0]], CHECKPOINT_HOURS
        for leg in self.legs[1:-1]:
            if leg.hours >= next_hour:
                picked.append(leg)
                next_hour = leg.hours + CHECKPOINT_HOURS
        top = self.top
        if all(abs(top.hours - leg.hours) > 0.3 for leg in picked):
            picked.append(top)
        picked.append(self.legs[-1])
        picked.sort(key=lambda leg: leg.hours)
        if len(picked) > MAX_CHECKPOINTS:
            # Равномерно по пути, но старт, финиш и высшая точка остаются
            step = (len(picked) - 1) / (MAX_CHECKPOINTS - 2)
            keep = {round(i * step) for i in range(MAX_CHECKPOINTS - 1)} | {picked.index(top)}
            picked = [leg for i, leg in enumerate(picked) if i in keep]
        return picked


def track(name: str, points: list[tuple[float, float, float]]) -> Track:
    """Время по участкам: горизонталь UP_KMH км/ч, плюс подъём UP_MH м/ч, плюс спуск DOWN_MH м/ч."""
    # Скользящее среднее по SMOOTH точкам: шум GPS и модели рельефа иначе раздувает набор высоты
    half = SMOOTH // 2
    smooth = [
        sum(p[2] for p in points[max(0, i - half):i + half + 1]) / len(points[max(0, i - half):i + half + 1])
        for i in range(len(points))
    ]
    points = [(lat, lon, ele) for (lat, lon, _), ele in zip(points, smooth)]
    legs = [Leg(points[0][0], points[0][1], points[0][2], 0.0, 0.0)]
    gain = loss = 0.0
    ref = points[0][2]          # высота, от которой считаем набор — без мелких колебаний
    for (lat1, lon1, _), (lat2, lon2, ele2) in zip(points, points[1:]):
        km = distance_km(lat1, lon1, lat2, lon2)
        up = down = 0.0
        if ele2 - ref >= ELE_NOISE:
            up, ref = ele2 - ref, ele2
        elif ref - ele2 >= ELE_NOISE:
            down, ref = ref - ele2, ele2
        gain, loss = gain + up, loss + down
        prev = legs[-1]
        hours = km / UP_KMH + up / UP_MH + down / DOWN_MH
        legs.append(Leg(lat2, lon2, ele2, prev.km + km, prev.hours + hours))
    return Track(name=name, legs=legs, gain=gain, loss=loss)


def start_options(now: datetime) -> list[tuple[str, datetime]]:
    """Варианты старта в местном времени: сейчас, завтра утром и ближайшие выходные."""
    day = now.replace(minute=0, second=0, microsecond=0)
    options = [("now", now.replace(second=0, microsecond=0))]
    tomorrow = (day + timedelta(days=1)).replace(hour=0)
    options += [(f"t{h}", tomorrow.replace(hour=h)) for h in (6, 8)]
    for target in (5, 6):                      # суббота, воскресенье
        delta = (target - now.weekday()) % 7
        if delta >= 2:
            options.append((f"w{target}", (day + timedelta(days=delta)).replace(hour=6)))
    return options[:5]
