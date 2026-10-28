"""Тексты всех экранов бота (HTML-разметка)."""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime
from html import escape

from bot import timeutil
from bot.db import User
from bot.services import AirQuality, Forecast, Report

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
MONTHS = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]

# Коды погоды WMO: (иконка днём, иконка ночью, описание)
WMO = {
    0: ("☀️", "🌙", "Ясно"),
    1: ("🌤", "🌙", "Преимущественно ясно"),
    2: ("⛅️", "☁️", "Переменная облачность"),
    3: ("☁️", "☁️", "Пасмурно"),
    45: ("🌫", "🌫", "Туман"),
    48: ("🌫", "🌫", "Туман с изморозью"),
    51: ("🌦", "🌧", "Слабая морось"),
    53: ("🌦", "🌧", "Морось"),
    55: ("🌧", "🌧", "Сильная морось"),
    56: ("🌧", "🌧", "Ледяная морось"),
    57: ("🌧", "🌧", "Сильная ледяная морось"),
    61: ("🌦", "🌧", "Небольшой дождь"),
    63: ("🌧", "🌧", "Дождь"),
    65: ("🌧", "🌧", "Сильный дождь"),
    66: ("🌧", "🌧", "Ледяной дождь"),
    67: ("🌧", "🌧", "Сильный ледяной дождь"),
    71: ("🌨", "🌨", "Небольшой снег"),
    73: ("🌨", "🌨", "Снег"),
    75: ("❄️", "❄️", "Сильный снег"),
    77: ("🌨", "🌨", "Снежные зёрна"),
    80: ("🌦", "🌧", "Небольшой ливень"),
    81: ("🌧", "🌧", "Ливень"),
    82: ("⛈", "⛈", "Сильный ливень"),
    85: ("🌨", "🌨", "Небольшой снегопад"),
    86: ("❄️", "❄️", "Сильный снегопад"),
    95: ("⛈", "⛈", "Гроза"),
    96: ("⛈", "⛈", "Гроза с градом"),
    99: ("⛈", "⛈", "Сильная гроза с градом"),
}

# Откуда дует ветер: (сокращение, стрелка — куда дует)
DIRECTIONS = [
    ("С", "↓"), ("СВ", "↙"), ("В", "←"), ("ЮВ", "↖"),
    ("Ю", "↑"), ("ЮЗ", "↗"), ("З", "→"), ("СЗ", "↘"),
]

BEAUFORT = [
    (0.3, "штиль"), (1.6, "тихий"), (3.4, "лёгкий"), (5.5, "слабый"), (8.0, "умеренный"),
    (10.8, "свежий"), (13.9, "сильный"), (17.2, "крепкий"), (20.8, "очень крепкий"),
    (24.5, "шторм"), (28.5, "сильный шторм"), (32.7, "жестокий шторм"),
]

UV_LEVELS = [(3, "низкий"), (6, "умеренный"), (8, "высокий"), (11, "очень высокий")]

PERIODS = {3: "Ночь", 9: "Утро", 15: "День", 21: "Вечер"}


@dataclass(frozen=True)
class AqiLevel:
    limit: int
    icon: str
    name: str
    advice: str
    sport: str
    windows: str
    mask: str
    purifier: str


# Шкала US AQI — та же, что в приложении IQAir
AQI_LEVELS = [
    AqiLevel(50, "🟢", "хорошо",
             "Воздух чистый — отличное время для прогулок и проветривания.",
             "можно", "открыть", "не нужна", "не нужен"),
    AqiLevel(100, "🟡", "умеренно",
             "Качество приемлемое. Очень чувствительным людям лучше не нагружаться долго на улице.",
             "можно", "можно открыть", "не нужна", "по желанию"),
    AqiLevel(150, "🟠", "вредно для чувствительных групп",
             "Детям, пожилым и людям с астмой или болезнями сердца лучше меньше бывать на улице.",
             "сократить", "закрыть", "чувствительным — да", "включить"),
    AqiLevel(200, "🔴", "вредно",
             "Ограничьте время на улице и откажитесь от тренировок на воздухе.",
             "избегать", "закрыть", "надеть", "включить"),
    AqiLevel(300, "🟣", "очень вредно",
             "Серьёзный риск для здоровья всех. Оставайтесь в помещении.",
             "избегать", "закрыть", "обязательно", "включить"),
    AqiLevel(10**6, "🟤", "опасно",
             "Чрезвычайное загрязнение. Не выходите на улицу без крайней необходимости.",
             "избегать", "закрыть", "обязательно (N95/FFP2)", "на максимум"),
]

EU_AQI_LEVELS = [
    (20, "хороший"), (40, "удовлетворительный"), (60, "умеренный"),
    (80, "плохой"), (100, "очень плохой"),
]

# Подпись, название и суточная норма ВОЗ 2021 (мкг/м³)
POLLUTANTS = {
    "pm2_5": ("PM2.5", "мелкие частицы", 15),
    "pm10": ("PM10", "крупные частицы", 45),
    "ozone": ("O₃", "озон", 100),
    "nitrogen_dioxide": ("NO₂", "диоксид азота", 25),
    "sulphur_dioxide": ("SO₂", "диоксид серы", 40),
    "carbon_monoxide": ("CO", "угарный газ", 4000),
    "dust": ("Пыль", "", None),
}

HOURS_PER_PAGE = 12
HOURLY_PAGES = 4


# ── форматирование ──────────────────────────────────────────────────────────

def weather(code: int | None, is_day: int | bool = True) -> tuple[str, str]:
    day_icon, night_icon, text = WMO.get(code, ("🌡", "🌡", "—"))
    return (day_icon if is_day else night_icon), text


def t(value: float | None) -> str:
    if value is None:
        return "—"
    r = round(value)
    return f"+{r}°" if r > 0 else f"−{-r}°" if r < 0 else "0°"


def num(value: float | None, digits: int = 0) -> str:
    if value is None:
        return "—"
    return f"{value:.{digits}f}".replace(".", ",")


def hm(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def date_label(d: date) -> str:
    return f"{WEEKDAYS[d.weekday()]}, {d.day} {MONTHS[d.month - 1]}"


def day_label(d: date, today: date) -> str:
    if d == today:
        return f"Сегодня, {d.day} {MONTHS[d.month - 1]}"
    if (d - today).days == 1:
        return f"Завтра, {d.day} {MONTHS[d.month - 1]}"
    return date_label(d)


def direction(degrees: float | None) -> tuple[str, str]:
    if degrees is None:
        return "", ""
    return DIRECTIONS[round(degrees / 45) % 8]


def beaufort(speed: float) -> str:
    return next((name for limit, name in BEAUFORT if speed < limit), "ураган")


def wind(speed: float | None, degrees: float | None, gusts: float | None = None) -> str:
    if speed is None:
        return "—"
    if round(speed) == 0:
        text = "штиль"
    else:
        short, arrow = direction(degrees)
        text = f"<b>{round(speed)} м/с</b> {short} {arrow} ({beaufort(speed)})"
    if gusts is not None and round(gusts) > max(round(speed), 0):
        text += f", порывы до {round(gusts)} м/с"
    return text


def pressure(hpa: float | None) -> str:
    if hpa is None:
        return "—"
    return f"{round(hpa * 0.750062)} мм рт. ст. ({round(hpa)} гПа)"


def visibility(meters: float) -> str:
    return f"{num(meters / 1000)} км" if meters >= 1000 else f"{round(meters)} м"


def uv_level(value: float) -> str:
    return next((name for limit, name in UV_LEVELS if value < limit), "экстремальный")


def uv(now: float | None, day_max: float | None) -> str:
    if now is None:
        return "—"
    if day_max is None:
        return f"{round(now)} ({uv_level(now)})"
    return f"{round(now)} сейчас, макс. {round(day_max)} ({uv_level(day_max)})"


def duration(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    minutes = round(seconds / 60)
    return f"{minutes // 60} ч {minutes % 60:02d} мин"


def precipitation(day: dict) -> str:
    total = day.get("precipitation_sum") or 0
    chance = day.get("precipitation_probability_max")
    if total >= 0.1:
        return f"осадки {num(total, 1)} мм" + (f" ({chance}%)" if chance is not None else "")
    if chance and chance >= 20:
        return f"вероятность осадков {chance}%"
    return "без осадков"


def aqi_level(aqi: float) -> AqiLevel:
    return next(level for level in AQI_LEVELS if aqi <= level.limit)


def eu_aqi_level(value: float) -> str:
    return next((name for limit, name in EU_AQI_LEVELS if value <= limit), "крайне плохой")


def concentration(value: float) -> str:
    return num(value, 0 if value >= 100 else 1)


def pollutant(air: AirQuality, key: str) -> str:
    label = POLLUTANTS.get(key, (key,))[0]
    value = air.pollutants.get(key)
    return f"{label} · {concentration(value)} мкг/м³" if value is not None else label


def place(user: User) -> str:
    return escape(user.place or "Моя местность")


# ── экраны ──────────────────────────────────────────────────────────────────

def welcome(name: str) -> str:
    return (
        f"👋 <b>Привет, {escape(name)}!</b>\n\n"
        "Я <b>AiroPost</b> — бот погоды и качества воздуха.\n\n"
        "Каждый день в удобное время пришлю сводку:\n"
        "🌡 температура и «ощущается как»\n"
        "💨 ветер, порывы и направление\n"
        "💧 влажность, давление, облачность, осадки\n"
        "🔆 УФ-индекс, восход и закат\n"
        "🌫 индекс качества воздуха AQI и загрязнители\n\n"
        "Для начала выберите местность 👇"
    )


def greeting(hour: int) -> str:
    if 5 <= hour < 12:
        text = "🌅 <b>Доброе утро!</b>"
    elif 12 <= hour < 17:
        text = "☀️ <b>Добрый день!</b>"
    elif 17 <= hour < 23:
        text = "🌆 <b>Добрый вечер!</b>"
    else:
        text = "🌙 <b>Доброй ночи!</b>"
    return f"{text} Ваша сводка погоды:"


def saved_header(user: User) -> str:
    text = "✅ <b>Местность сохранена!</b>"
    if user.notify_enabled:
        text += f"\nСводка будет приходить каждый день в {user.notify_time}."
    return text


def home(user: User, report: Report, header: str | None = None) -> str:
    fc = report.forecast
    c = fc.current
    now = fc.local_now()
    today = fc.daily[0] if fc.daily else {}
    icon, desc = weather(c.get("weather_code"), c.get("is_day", 1))

    lines = [header, ""] if header else []
    lines += [
        f"📍 <b>{place(user)}</b>",
        f"<i>{date_label(now)}, {hm(now)}</i>",
        "",
        f"{icon} <b>{t(c.get('temperature_2m'))}</b>  {desc}",
        f"🤗 Ощущается как {t(c.get('apparent_temperature'))}",
    ]
    if today:
        lines.append(
            f"🗓 Сегодня {t(today.get('temperature_2m_min'))} … {t(today.get('temperature_2m_max'))}, "
            f"{precipitation(today)}"
        )

    cloud = f"☁️ Облачность: {num(c.get('cloud_cover'))}%"
    if c.get("visibility") is not None:
        cloud += f" · видимость {visibility(c['visibility'])}"
    lines += [
        "",
        f"💨 Ветер: {wind(c.get('wind_speed_10m'), c.get('wind_direction_10m'), c.get('wind_gusts_10m'))}",
        f"💧 Влажность: {num(c.get('relative_humidity_2m'))}% · точка росы {t(c.get('dew_point_2m'))}",
        f"🧭 Давление: {pressure(c.get('surface_pressure'))}",
        cloud,
        f"🔆 УФ-индекс: {uv(c.get('uv_index'), today.get('uv_index_max'))}",
    ]
    if today.get("sunrise") and today.get("sunset"):
        lines.append(
            f"🌅 Восход {hm(today['sunrise'])} · закат {hm(today['sunset'])} · "
            f"день {duration(today.get('daylight_duration'))}"
        )

    periods = upcoming_periods(fc, now)
    if periods:
        lines += ["", "<b>Дальше</b>", *periods]

    lines += ["", *air_summary(report.air), "", schedule_line(user)]
    return "\n".join(lines)


def upcoming_periods(fc: Forecast, now: datetime, count: int = 4) -> list[str]:
    result = []
    for h in fc.upcoming_hours(now):
        label = PERIODS.get(h["time"].hour)
        if not label:
            continue
        icon, _ = weather(h.get("weather_code"), h.get("is_day", 1))
        result.append(
            f"{label} {icon} <b>{t(h.get('temperature_2m'))}</b> · "
            f"💧{num(h.get('precipitation_probability'))}% · 💨{num(h.get('wind_speed_10m'))} м/с"
        )
        if len(result) == count:
            break
    return result


def air_summary(air: AirQuality | None) -> list[str]:
    if not air or air.aqi is None:
        return ["🌫 Данные о качестве воздуха временно недоступны"]
    level = aqi_level(air.aqi)
    lines = [f"{level.icon} <b>Воздух: AQI {round(air.aqi)}</b> — {level.name}"]
    if air.main_pollutant:
        lines.append(f"Основной загрязнитель: {pollutant(air, air.main_pollutant)}")
    lines.append(f"💡 {level.advice}")
    return lines


def schedule_line(user: User) -> str:
    if user.notify_enabled:
        return f"🔔 Сводка каждый день в {user.notify_time}"
    return "🔕 Ежедневная сводка выключена"


def hourly_pages(fc: Forecast) -> int:
    return max(1, min(HOURLY_PAGES, math.ceil(len(fc.upcoming_hours()) / HOURS_PER_PAGE)))


def hourly(user: User, fc: Forecast, page: int) -> str:
    now = fc.local_now()
    hours = fc.upcoming_hours(now)[page * HOURS_PER_PAGE:(page + 1) * HOURS_PER_PAGE]
    lines = [
        "🕐 <b>Почасовой прогноз</b>",
        f"📍 {place(user)}",
        "<i>температура (ощущается) · осадки · ветер</i>",
    ]
    current_day = None
    for h in hours:
        day = h["time"].date()
        if day != current_day:
            current_day = day
            lines += ["", f"<b>{day_label(day, now.date())}</b>"]
        icon, _ = weather(h.get("weather_code"), h.get("is_day", 1))
        speed = h.get("wind_speed_10m")
        _, arrow = direction(h.get("wind_direction_10m")) if speed and round(speed) else ("", "")
        rain = f"💧{num(h.get('precipitation_probability'))}%"
        if (h.get("precipitation") or 0) >= 0.1:
            rain += f" {num(h['precipitation'], 1)} мм"
        lines.append(
            f"<code>{hm(h['time'])}</code> {icon} <b>{t(h.get('temperature_2m'))}</b> "
            f"({t(h.get('apparent_temperature'))}) · {rain} · 💨{num(speed)} м/с {arrow}".rstrip()
        )
    return "\n".join(lines)


def daily(user: User, fc: Forecast) -> str:
    today = fc.local_now().date()
    lines = ["📅 <b>Прогноз на 7 дней</b>", f"📍 {place(user)}"]
    for d in fc.daily:
        icon, desc = weather(d.get("weather_code"))
        short, arrow = direction(d.get("wind_direction_10m_dominant"))
        lines += [
            "",
            f"<b>{day_label(d['time'], today)}</b> — {icon} {desc}",
            f"🌡 {t(d.get('temperature_2m_min'))} … {t(d.get('temperature_2m_max'))} · {precipitation(d)}",
            f"💨 {short} {arrow} до {num(d.get('wind_speed_10m_max'))} м/с, "
            f"порывы {num(d.get('wind_gusts_10m_max'))} · 🔆 УФ {num(d.get('uv_index_max'))}",
        ]
    return "\n".join(lines)


def air_details(user: User, air: AirQuality | None) -> str:
    lines = ["🌫 <b>Качество воздуха</b>", f"📍 {place(user)}", ""]
    if not air or air.aqi is None:
        lines.append("Данные временно недоступны. Попробуйте обновить через пару минут.")
        return "\n".join(lines)

    level = aqi_level(air.aqi)
    lines.append(f"{level.icon} <b>AQI {round(air.aqi)}</b> (US) — {level.name}")
    if air.main_pollutant:
        lines.append(f"Основной загрязнитель: <b>{pollutant(air, air.main_pollutant)}</b>")
    if air.eu_aqi is not None:
        lines.append(f"🇪🇺 Европейский индекс: {round(air.eu_aqi)} — {eu_aqi_level(air.eu_aqi)}")
    source = air.source + (f" · {escape(air.station)}" if air.station else "")
    lines.append(f"<i>Источник: {source}</i>")

    measured = [(k, v) for k, v in air.pollutants.items() if v is not None]
    if measured:
        lines += ["", "<b>Загрязнители</b> <i>(× суточной нормы ВОЗ)</i>"]
        for key, value in measured:
            label, title, norm = POLLUTANTS[key]
            mark = ""
            if norm:
                ratio = value / norm
                mark = f" ⚠️ ×{num(ratio, 1)}" if ratio > 1 else " ✅"
            title = f" {title}" if title else ""
            lines.append(f"• <b>{label}</b>{title} — {concentration(value)} мкг/м³{mark}")

    lines += [
        "",
        "<b>Рекомендации</b>",
        f"🚴 Спорт на улице: {level.sport}",
        f"🪟 Окна: {level.windows}",
        f"😷 Маска: {level.mask}",
        f"🌀 Очиститель воздуха: {level.purifier}",
        f"💡 {level.advice}",
    ]

    now = air.local_now().replace(minute=0, second=0, microsecond=0)
    upcoming = [
        h for h in air.hourly
        if h["time"] > now and h["time"].hour % 3 == 0 and h.get("us_aqi") is not None
    ][:8]
    if upcoming:
        cells = [f"{hm(h['time'])} {aqi_level(h['us_aqi']).icon}{round(h['us_aqi'])}" for h in upcoming]
        lines += ["", "<b>Прогноз AQI</b> <i>(модель CAMS)</i>"]
        lines += ["  ".join(cells[i:i + 4]) for i in range(0, len(cells), 4)]

    lines += [
        "",
        "<i>Шкала: 🟢 0–50 · 🟡 51–100 · 🟠 101–150 · 🔴 151–200 · 🟣 201–300 · 🟤 300+</i>",
    ]
    return "\n".join(lines)


def settings(user: User) -> str:
    lines = [
        "⚙️ <b>Настройки</b>",
        "",
        f"📍 Местность: <b>{escape(user.place) if user.place else 'не выбрана'}</b>",
        f"⏰ Время сводки: <b>{user.notify_time}</b>" + (f" <i>({escape(user.tz)})</i>" if user.tz else ""),
        f"🔔 Ежедневная сводка: <b>{'включена' if user.notify_enabled else 'выключена'}</b>",
    ]
    upcoming = timeutil.next_send(user)
    if upcoming:
        today = timeutil.local_now(user.tz).date()
        when = "сегодня" if upcoming.date() == today else "завтра"
        lines.append(f"📬 Следующая сводка: {when} в {hm(upcoming)}")
    return "\n".join(lines)


def time_hours(user: User, error: bool = False) -> str:
    lines = [
        "⏰ <b>Время ежедневной сводки</b>",
        "",
        f"Сейчас: <b>{user.notify_time}</b>" + (f" <i>(местное, {escape(user.tz)})</i>" if user.tz else ""),
        "Выберите час 👇",
        "",
        "<i>Или отправьте время сообщением, например 07:30</i>",
    ]
    if error:
        lines.insert(0, "❗️ Не понял время. Напишите в формате ЧЧ:ММ, например 07:30\n")
    return "\n".join(lines)


def time_minutes(hour: int) -> str:
    return f"⏰ <b>Время ежедневной сводки</b>\n\nЧас: <b>{hour:02d}</b>\nТеперь выберите минуты 👇"


def location_prompt() -> str:
    return (
        "📍 <b>Выбор местности</b>\n\n"
        "Напишите название города или населённого пункта,\n"
        "например: <i>Ташкент</i>, <i>Самарканд</i>, <i>Москва</i>.\n"
        "Можно уточнить страну: <i>Бухара, Узбекистан</i>.\n\n"
        "Или нажмите <b>«📍 Отправить геолокацию»</b> под полем ввода — "
        "прогноз будет точно для вашего места."
    )


LOCATION_KEYBOARD_HINT = "⌨️ Кнопка геолокации — под полем ввода 👇"


def searching(query: str) -> str:
    return f"🔎 Ищу «{escape(query)}»…"


def locating() -> str:
    return "📡 Определяю местность…"


def search_results(query: str) -> str:
    return f"🔎 По запросу «{escape(query)}» нашлось несколько мест.\n\nВыберите нужное 👇"


def not_found(query: str) -> str:
    return (
        f"😕 Не нашёл «{escape(query)}».\n\n"
        "Проверьте написание или попробуйте другое название — например, ближайший крупный город. "
        "Можно просто отправить геолокацию."
    )


def search_expired() -> str:
    return "Результаты поиска устарели — отправьте название ещё раз."


def error() -> str:
    return (
        "⚠️ <b>Не удалось получить данные о погоде</b>\n\n"
        "Сервис погоды временно недоступен. Попробуйте через минуту."
    )
