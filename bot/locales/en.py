STRINGS = {
    "lang_name": "🇬🇧 English",
    "decimal": ".",

    # ── dates ──
    "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "date": "{wd}, {m} {d}",
    "day_month": "{m} {d}",
    "today": "Today",
    "tomorrow": "Tomorrow",

    # ── weather ──
    "wmo": {
        0: "Clear sky", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Freezing fog",
        51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
        56: "Freezing drizzle", 57: "Heavy freezing drizzle",
        61: "Light rain", 63: "Rain", 65: "Heavy rain",
        66: "Freezing rain", 67: "Heavy freezing rain",
        71: "Light snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains",
        80: "Light showers", 81: "Showers", 82: "Heavy showers",
        85: "Light snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm with hail",
    },
    "directions": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
    "beaufort": [
        "calm", "light air", "light breeze", "gentle breeze", "moderate breeze", "fresh breeze",
        "strong breeze", "near gale", "gale", "strong gale", "storm", "violent storm", "hurricane",
    ],
    "uv_levels": ["low", "moderate", "high", "very high", "extreme"],
    "periods": {3: "Night", 9: "Morning", 15: "Afternoon", 21: "Evening"},

    # ── units ──
    "ms": "m/s",
    "mm": "mm",
    "km": "km",
    "m": "m",
    "ug": "µg/m³",
    "pressure": "{hpa} hPa ({mm} mmHg)",
    "duration": "{h} h {m:02d} min",

    # ── air quality: name, advice, sport, windows, mask, purifier ──
    "aqi_levels": [
        ("good", "The air is clean — a great time for a walk and to air out your home.",
         "fine", "open", "not needed", "not needed"),
        ("moderate", "Air quality is acceptable. Unusually sensitive people should limit long outdoor exertion.",
         "fine", "can be open", "not needed", "optional"),
        ("unhealthy for sensitive groups",
         "Children, older adults and people with asthma or heart disease should spend less time outdoors.",
         "reduce", "close", "for sensitive groups", "turn on"),
        ("unhealthy", "Limit time outdoors and skip outdoor workouts.",
         "avoid", "close", "wear one", "turn on"),
        ("very unhealthy", "Serious health risk for everyone. Stay indoors.",
         "avoid", "close", "required", "turn on"),
        ("hazardous", "Emergency conditions. Do not go outside unless you have to.",
         "avoid", "close", "required (N95/FFP2)", "maximum"),
    ],
    "eu_aqi_levels": ["good", "fair", "moderate", "poor", "very poor", "extremely poor"],
    "pollutants": {
        "pm2_5": "fine particles", "pm10": "coarse particles", "ozone": "ozone",
        "nitrogen_dioxide": "nitrogen dioxide", "sulphur_dioxide": "sulphur dioxide",
        "carbon_monoxide": "carbon monoxide", "dust": "",
    },
    "dust": "Dust",

    # ── fragments ──
    "calm": "calm",
    "gusts": "gusts up to {g} m/s",
    "uv_now_max": "{now} now, max {max} ({level})",
    "precip_sum": "precipitation {mm} mm",
    "precip_chance": "{p}% chance of precipitation",
    "no_precip": "no precipitation",
    "my_place": "My location",

    # ── welcome and digest ──
    "welcome": (
        "👋 <b>Hi, {name}!</b>\n\n"
        "I'm <b>AiroPost</b>, a weather and air quality bot.\n\n"
        "Every day at a time you choose, I'll send you a summary:\n"
        "🌡 temperature and feels-like\n"
        "💨 wind, gusts and direction\n"
        "💧 humidity, pressure, cloud cover, precipitation\n"
        "🔆 UV index, sunrise and sunset\n"
        "🌫 air quality index (AQI) and pollutants\n\n"
        "To start, choose your location 👇"
    ),
    "greet_morning": "🌅 <b>Good morning!</b>",
    "greet_day": "☀️ <b>Good afternoon!</b>",
    "greet_evening": "🌆 <b>Good evening!</b>",
    "greet_night": "🌙 <b>Good night!</b>",
    "greet_suffix": "Here's your weather summary:",
    "saved": "✅ <b>Location saved!</b>",
    "saved_schedule": "You'll get a summary every day at {time}.",

    # ── home screen ──
    "feels": "🤗 Feels like {t}",
    "today_range": "🗓 Today {min} … {max}, {precip}",
    "wind_line": "💨 Wind: {wind}",
    "humidity": "💧 Humidity: {h}% · dew point {dew}",
    "pressure_line": "🧭 Pressure: {p}",
    "clouds": "☁️ Cloud cover: {c}%",
    "visibility": " · visibility {v}",
    "uv_line": "🔆 UV index: {uv}",
    "sun": "🌅 Sunrise {rise} · sunset {set} · daylight {len}",
    "next": "<b>Coming up</b>",
    "air_unavailable": "🌫 Air quality data is temporarily unavailable",
    "air_short": "<b>Air: AQI {aqi}</b> — {level}",
    "main_pollutant": "Main pollutant: {p}",
    "schedule_on": "🔔 Summary every day at {time}",
    "schedule_off": "🔕 Daily summary is off",

    # ── forecasts ──
    "hourly_title": "🕐 <b>Hourly forecast</b>",
    "hourly_legend": "<i>temperature (feels like) · precipitation · wind</i>",
    "daily_title": "📅 <b>7-day forecast</b>",
    "daily_wind": "💨 {dir} {arrow} up to {max} m/s, gusts {g} · 🔆 UV {uv}",

    # ── air ──
    "air_title": "🌫 <b>Air quality</b>",
    "air_na": "Data is temporarily unavailable. Try refreshing in a couple of minutes.",
    "aqi_line": "<b>AQI {aqi}</b> (US) — {level}",
    "eu_line": "🇪🇺 European index: {v} — {level}",
    "source": "Source: {s}",
    "pollutants_title": "<b>Pollutants</b> <i>(× WHO 24-hour guideline)</i>",
    "advice_title": "<b>Recommendations</b>",
    "sport": "🚴 Outdoor exercise: {v}",
    "windows": "🪟 Windows: {v}",
    "mask": "😷 Mask: {v}",
    "purifier": "🌀 Air purifier: {v}",
    "aqi_forecast": "<b>AQI forecast</b> <i>(CAMS model)</i>",
    "scale": "<i>Scale: 🟢 0–50 · 🟡 51–100 · 🟠 101–150 · 🔴 151–200 · 🟣 201–300 · 🟤 300+</i>",

    # ── settings ──
    "settings_title": "⚙️ <b>Settings</b>",
    "s_place": "📍 Location: <b>{p}</b>",
    "s_place_none": "not set",
    "s_time": "⏰ Summary time: <b>{time}</b>",
    "s_notify": "🔔 Daily summary: <b>{state}</b>",
    "on": "on",
    "off": "off",
    "s_next": "📬 Next summary: {when} at {time}",
    "today_l": "today",
    "tomorrow_l": "tomorrow",
    "s_lang": "🌐 Language: {name}",
    "lang_title": "🌐 <b>Choose language</b>\nВыберите язык · Tilni tanlang",

    # ── time ──
    "time_title": "⏰ <b>Daily summary time</b>",
    "time_current": "Current: <b>{time}</b>",
    "time_local": " <i>(local, {tz})</i>",
    "pick_hour": "Choose the hour 👇",
    "time_hint": "<i>Or send the time as a message, e.g. 07:30</i>",
    "time_error": "❗️ I didn't get that time. Use HH:MM, e.g. 07:30\n",
    "time_hour": "Hour: <b>{h}</b>",
    "pick_minutes": "Now choose the minutes 👇",
    "time_saved": "✅ You'll get the summary at <b>{time}</b>",

    # ── location ──
    "location_prompt": (
        "📍 <b>Choose location</b>\n\n"
        "Type the name of a city or town,\n"
        "for example: <i>Tashkent</i>, <i>London</i>, <i>New York</i>.\n"
        "You can add the country: <i>Bukhara, Uzbekistan</i>.\n\n"
        "Or tap <b>“📍 Send my location”</b> below the input field "
        "to get a forecast for exactly where you are."
    ),
    "location_keyboard_hint": "⌨️ The location button is below the input field 👇",
    "searching": "🔎 Searching for “{q}”…",
    "locating": "📡 Detecting your location…",
    "search_results": "🔎 Found several places for “{q}”.\n\nChoose one 👇",
    "not_found": (
        "😕 Couldn't find “{q}”.\n\n"
        "Check the spelling or try another name, such as the nearest large city. "
        "You can also just send your location."
    ),
    "error": (
        "⚠️ <b>Couldn't get weather data</b>\n\n"
        "The weather service is temporarily unavailable. Please try again in a minute."
    ),

    # ── buttons ──
    "btn_pick_place": "📍 Choose location",
    "btn_change_place": "📍 Change location",
    "btn_refresh": "🔄 Refresh",
    "btn_hourly": "🕐 Hourly",
    "btn_daily": "📅 7 days",
    "btn_air": "🌫 Air quality",
    "btn_settings": "⚙️ Settings",
    "btn_back": "⬅️ Back",
    "btn_cancel": "⬅️ Cancel",
    "btn_earlier": "◀️ Earlier",
    "btn_later": "Later ▶️",
    "btn_time": "⏰ Summary time: {time}",
    "btn_notify_off": "🔕 Turn off summary",
    "btn_notify_on": "🔔 Turn on summary",
    "btn_lang": "🌐 Language · Язык · Til",
    "btn_send_location": "📍 Send my location",
    "btn_search_again": "📍 Search again",
    "btn_retry": "🔄 Try again",
    "placeholder": "City name…",

    # ── toasts ──
    "t_refreshed": "🔄 Updated",
    "t_on": "🔔 Summary turned on",
    "t_off": "🔕 Summary turned off",
    "t_saved": "✅ Location saved",
    "t_time": "✅ Summary will arrive at {time}",
    "t_search_expired": "Search results expired — please send the name again.",
    "t_stale": "This button is outdated — send /start",
    "t_lang": "✅ English",

    # ── commands ──
    "cmd_start": "🌤 Current weather",
    "cmd_location": "📍 Change location",
    "cmd_settings": "⚙️ Settings and summary time",
    "cmd_language": "🌐 Language",
}
