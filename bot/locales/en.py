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
    "coords_hint": "🧭 Or coordinates as text: <code>41.49519, 70.058671</code> — copy them from any map app.",
    "coords_error": "❗️ I couldn't read those coordinates. Example: <code>41.49519, 70.058671</code>\n",
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

# ── mountains ──
STRINGS.update({
    "m_title": "⛰ <b>Mountains</b>",
    "m_intro": (
        "Forecasts for summits: temperature and wind at different altitudes, freezing level, "
        "precipitation, thunderstorms and the best days to climb."
    ),
    "m_empty": "No saved peaks yet. Add your first one 👇",
    "m_saved": "Saved peaks:",
    "m_add_prompt": (
        "⛰ <b>New peak</b>\n\n"
        "Type the name of a peak or pass, for example: <i>Big Chimgan</i>, "
        "<i>Lenin Peak</i>, <i>Elbrus</i>.\n\n"
        "Or send a point on the map: 📎 → <b>Location</b> → move the pin to the summit → "
        "<b>“Send selected location”</b>."
    ),
    "m_searching": "🔎 Searching for the peak “{q}”…",
    "m_results": "🔎 Results for “{q}”. Choose a peak 👇",
    "m_not_found": (
        "😕 Couldn't find the peak “{q}”.\n\n"
        "Try another spelling (Katta Chimyon, Большой Чимган) or send a point on the map."
    ),
    "m_point_name": "Point {lat}, {lon}",
    "m_snapped": "📍 The pin was snapped to the nearest OpenStreetMap peak — name and elevation come from there.",
    "m_pin_hint": (
        "ℹ️ The {ele} m height comes from a terrain map and can be too low for sharp summits. "
        "Correct it or rename the peak with ✏️ Edit."
    ),
    "m": "m",
    "m_now": "<b>Summit now</b> · {time}",
    "m_temp": "🌡 <b>{t}</b> · feels like {feels}",
    "m_wind": "💨 Wind <b>{v} m/s</b> {dir} {arrow}",
    "m_in_cloud": "🌫 Summit in cloud — poor visibility",
    "m_precip": "{icon} {phase} {mm} mm/h · {p}% chance",
    "m_no_precip": "☀️ No precipitation · {p}% chance",
    "m_snow": "snow",
    "m_sleet": "sleet",
    "m_rain": "rain",
    "m_fl": "🧊 Freezing level: <b>{h} m</b>",
    "m_fl_below": " — below freezing on the summit",
    "m_fl_above": " — above the summit",
    "m_storm": "⚡️ Thunderstorm risk: {level}",
    "m_storm_levels": ["low", "moderate", "high"],
    "m_thunder_now": "⛈ <b>Thunderstorm!</b>",
    "m_uv": "🔆 Daytime UV up to {uv} adjusted for altitude — sunglasses and sunscreen are a must",
    "m_sun": "🌅 Sunrise {rise} · sunset {set}",
    "m_windows": "<b>Climbing windows</b>",
    "m_good": "good window",
    "m_caution": "use caution",
    "m_bad": "not recommended",
    "r_thunder": "thunderstorm from {time}",
    "r_storm_risk": "storm risk from {time}",
    "r_wind": "wind up to {v} m/s",
    "r_precip": "{phase} {mm} mm",
    "r_prob": "{p}% precipitation",
    "r_cold": "feels like {t}",
    "r_cloud": "in cloud {h} h",
    "m_updated": "<i>Data as of {time}. Model forecast for {ele} m.</i>",
    "m_profile_title": "📊 <b>Altitude profile</b> · {name}",
    "m_profile_legend": "<i>altitude · temperature (feels like) · wind · precipitation</i>",
    "m_fl_row": "── 🧊 0° at {h} m ──",
    "m_you": " (you)",
    "m_profile_note": (
        "<i>Free-air temperature from the model. Sunny slopes can be warmer in the daytime "
        "and valleys colder at night.</i>"
    ),
    "m_hourly_title": "🕐 <b>Summit hourly</b> · {name} ({ele} m)",
    "m_hourly_legend": "<i>temperature (feels like) · wind · precipitation</i>",
    "m_outlook_title": "📅 <b>Climbing windows</b> · {name}",
    "m_outlook_day": "🌡 {tmin}…{tmax} (feels like {feels}) · 💨 up to {wind} m/s",
    "m_outlook_fl": " · 🧊 0° {lo}–{hi} m",
    "m_outlook_note": "<i>Rated on daytime hours 06–18 at summit height.</i>",
    "m_precip_none": "☀️ no precipitation",
    "m_route_prompt": (
        "🧗 <b>I'm on the route</b> · {name}\n\n"
        "Send your location with the button below — I'll show the weather here, on the summit "
        "and at the altitudes in between.\n\n"
        "<i>Even a weak connection is enough: the answer is one short message.</i>"
    ),
    "m_route_hint": "⌨️ The “Send my location” button is below the input field 👇",
    "m_route_title": "🧗 <b>On the route</b> · {name}",
    "m_route_you": "📍 You: <b>{ele} m</b> · {km} km and {climb} m to the summit",
    "m_route_top": "📍 You're at the summit: <b>{ele} m</b>",
    "m_route_sun": "🕐 {time} · sunset {set}, {left} of daylight left",
    "m_route_dark": "🌙 {time} · it's dark, sunrise at {rise}",
    "m_here": "<b>Here:</b> {icon} {t}, feels like {feels}, wind {v} m/s",
    "m_summit_short": "<b>Summit:</b> {t}, feels like {feels}, wind {v} m/s",
    "m_way_up": "<b>On the way up</b>",
    "m_next_hours": "<b>Summit in the next hours</b>",
    "m_warnings": "<b>⚠️ Heads up</b>",
    "w_dark": "less than {h} h until sunset — plan your descent",
    "w_wind": "summit wind rising to {v} m/s by {time}",
    "w_storm": "thunderstorm risk by {time}",
    "w_precip": "{phase} on the summit by {time}",
    "w_cold": "summit feels like {t}",
    "w_cloud": "summit going into cloud by {time}",
    "m_all_good": "✅ Summit weather looks stable for the next hours",
    "m_offline_header": (
        "📥 <b>Offline forecast</b> · {name} ({ele} m)\n"
        "<i>Saved {date}, {time}. The bot will not delete this message.</i>"
    ),
    "m_ele_prompt": (
        "✏️ <b>{name}</b> · {ele} m\n\n"
        "Send the exact elevation as a number, e.g. <i>3309</i>, or a new name as text."
    ),
    "m_ele_error": "❗️ The elevation must be a number from 100 to 8900 m.\n",
    "m_delete_confirm": "🗑 Delete the peak <b>{name}</b>?",

    "btn_mountains": "⛰ Mountains",
    "btn_m_add": "➕ Add a peak",
    "btn_m_profile": "📊 Altitude profile",
    "btn_m_hourly": "🕐 Hourly",
    "btn_m_outlook": "📅 7-day windows",
    "btn_m_route": "🧗 I'm on the route",
    "btn_m_offline": "📥 Save offline",
    "btn_m_ele": "✏️ Edit",
    "btn_m_delete": "🗑 Delete",
    "btn_m_back": "⬅️ To peaks",
    "btn_m_to_peak": "⬅️ To the peak",
    "btn_m_yes_delete": "🗑 Yes, delete",
    "btn_m_route_again": "📍 Update location",
    "btn_m_minus": "◀️ −3 h",
    "btn_m_plus": "+3 h ▶️",
    "btn_m_now": "🕐 Now",

    "t_m_limit": "You can save up to {n} peaks — delete one first.",
    "t_m_added": "⛰ Peak added",
    "t_m_saved": "📥 Forecast saved to the chat — available offline",
    "t_m_ele": "✅ Elevation: {ele} m",
    "t_m_renamed": "✅ Name changed",
    "t_m_deleted": "🗑 Peak deleted",
    "t_m_missing": "Peak not found — open the list again.",
})

# ── peak catalog and moderation ──
STRINGS.update({
    "m_private_note": "🔒 Your peaks are visible only to you.",
    "m_catalog_btn": "🏔 Peaks of Uzbekistan ({n})",
    "m_catalog_title": "🏔 <b>Peaks of Uzbekistan</b>",
    "m_catalog_intro": (
        "The main peaks for hiking and climbing — open to everyone. "
        "You can suggest your own peak for the catalog with the 📢 button on its page."
    ),
    "m_catalog_page": "<i>Page {p} of {n}</i>",
    "region_tashkent": "Tashkent Region",
    "region_jizzakh": "Jizzakh Region",
    "region_surkhandarya": "Surkhandarya Region",
    "region_community": "Added by users",
    "st_private": "🔒 Visible only to you",
    "st_pending": "⏳ Waiting for admin review",
    "st_approved": "✅ Published in the catalog",
    "st_rejected": "❌ Publication rejected — you can submit it again",
    "st_catalog": "🏔 Peaks of Uzbekistan catalog",
    "st_community": "🏔 Catalog · suggested by a user",
    "m_publish_confirm": (
        "📢 <b>Publish “{name}”?</b>\n\n"
        "⛰ {ele} m · 📍 <code>{lat}, {lon}</code>\n\n"
        "An admin will review the peak. Once approved, it appears in the “Peaks of Uzbekistan” "
        "catalog and every user of the bot can see it."
    ),
    "m_published_notice": (
        "✅ <b>Your peak “{name}” has been published!</b>\n"
        "Everyone can now see it in the “Peaks of Uzbekistan” catalog."
    ),
    "m_rejected_notice": (
        "❌ <b>Publication of “{name}” was rejected.</b>\n"
        "The peak stays in your list — it is visible only to you."
    ),
    "btn_m_publish": "📢 Publish",
    "btn_m_publish_yes": "✅ Send for review",
    "btn_m_catalog_back": "⬅️ To the catalog",
    "t_m_sent": "⏳ Sent to the admin for review",
    "t_m_duplicate": "This peak is already in the catalog or under review: {name}",
    "t_m_pending": "Already under review",
    "t_m_no_admin": "Couldn't reach the admin — please try again later",
    "t_m_readonly": "This peak is from the shared catalog and can't be changed",

    "a_request": (
        "📢 <b>Publication request #{id}</b>\n\n"
        "⛰ <b>{name}</b> · {ele} m\n"
        "📍 <code>{lat}, {lon}</code>\n"
        "🗺 <a href=\"{map}\">Open on the map</a>\n"
        "👤 {author}"
    ),
    "a_approved": "✅ <b>Published</b> — {admin}",
    "a_rejected": "❌ <b>Rejected</b> — {admin}",
    "a_no_pending": "📭 No requests waiting for review.",
    "btn_a_approve": "✅ Publish",
    "btn_a_reject": "❌ Reject",
    "t_a_done": "This request has already been reviewed",
    "t_a_forbidden": "Admins only",
    "t_a_approved": "✅ Published",
    "t_a_rejected": "❌ Rejected",
})


# ── route timing, what to pack, weekend, SOS, links ──
STRINGS.update({
    "m_plan_up": "⏱ Ascent ≈ {d} → at the summit ≈ {at}",
    "m_plan_down": "↩️ Descent back here ≈ {d} → here ≈ {at}",
    "m_plan_latest": "🔙 To get back here before sunset, leave the summit by {time}",
    "m_plan_note": "<i>Travel time at an average pace: 4 km/h and 400 m of ascent per hour, no breaks.</i>",
    "w_turnaround": "not enough daylight to summit and return — turn around by {time}",
    "w_storm_before": "thunderstorm by {time} — before you reach the summit (≈ {at})",
    "m_best": "🕐 best {span}",

    "m_gear_title": "🎒 <b>What to pack</b> · {name}",
    "m_gear_summary": "At the summit: 🌡 {tmin}…{tmax} (feels like down to {feels}) · 💨 up to {wind} m/s",
    "m_gear_snow": "❄️ Fresh snow on the summit over the last 3 days: ≈ {cm} cm",
    "m_gear_note": (
        "<i>Packed {n} of {total}. Tick items with the buttons below. "
        "The list is based on the forecast at summit height.</i>"
    ),
    "g_water": "💧 Water",
    "g_food": "🍫 Food and snacks",
    "g_headlamp": "🔦 Headlamp",
    "g_power": "🔋 Power bank",
    "g_firstaid": "🩹 First aid kit",
    "g_glasses": "🕶 Sunglasses",
    "g_sunscreen": "🧴 SPF 50 sunscreen",
    "g_cap": "🧢 Cap or sun hat",
    "g_beanie": "🧣 Beanie and buff",
    "g_gloves": "🧤 Gloves",
    "g_fleece": "🧥 Fleece",
    "g_down": "🪶 Down jacket",
    "g_mittens": "🥶 Mittens and balaclava",
    "g_windproof": "🌬 Windbreaker",
    "g_rain": "☔️ Rain shell",
    "g_drybag": "🎒 Dry bag",
    "g_crampons": "⛓ Crampons or microspikes",
    "g_poles": "🦯 Trekking poles",
    "g_gaiters": "🥾 Gaiters",
    "g_axe": "⛏ Ice axe and helmet",
    "g_thermos": "♨️ Thermos",
    "gr_water": "at least 2 L per person",
    "gr_water_hot": "hot — at least 3 L per person",
    "gr_headlamp": "sunset at {time}; bring it even if you plan to be back in daylight",
    "gr_power": "and save the offline forecast in advance",
    "gr_poles": "they save your knees on the descent",
    "gr_feels": "feels like down to {t} at the summit",
    "gr_wind": "wind up to {v} m/s",
    "gr_precip": "{phase} up to {mm} mm",
    "gr_prob": "{p}% chance of precipitation",
    "gr_ice_snow": "frost and ≈ {cm} cm of fresh snow at the summit — slopes may be icy",
    "gr_ice_winter": "winter: snow and ice above the freezing level",
    "gr_snow": "snow on the trail",
    "gr_axe": "steep snow slopes above 3500 m",
    "gr_uv": "UV up to {uv} at the summit",
    "gr_glare": "snow glare — category 3–4 lenses",
    "gr_sun": "sun and heat on the approach",
    "gn_bad": "❌ Not a recommended day for a climb — better pick another date.",
    "gn_storm": "⛈ Thunderstorm from {time}: start early and get off the ridge and summit before it begins.",
    "gn_best": "🕐 Calmest hours at the summit: {span}",
    "gn_altitude": (
        "🏔 Altitude sickness is possible above 3000 m: gain height slowly and drink more. "
        "Severe headache, nausea, breathlessness at rest — go down immediately."
    ),
    "btn_m_gear": "🎒 What to pack",

    "btn_m_weekend": "🗓 Where to go this weekend",
    "m_weekend_title": "🗓 <b>Where to go this weekend</b> · {days}",
    "m_weekend_intro": (
        "<i>Catalog peaks and yours — best first. Rated by daytime hours 06–18 at summit height.</i>"
    ),
    "m_weekend_empty": "😕 The forecast for peaks is unavailable right now. Try again in a couple of minutes.",
    "m_weekend_loading": "🔎 Checking the weather on the peaks…",
    "m_digest_header": "🔔 <b>Weekend forecast</b> · {days}",
    "m_digest_note": (
        "<i>I'll let you know if the forecast changes noticeably. To unsubscribe, tap 🔕 on the peak page.</i>"
    ),
    "m_change_header": "🔔 <b>The weekend forecast has changed</b>",
    "btn_m_sub": "🔔 Send me the weekend forecast",
    "btn_m_unsub": "🔕 Stop the weekend forecast",
    "t_m_sub": (
        "🔔 Done! The weekend forecast for this peak will arrive on Thursday evening, "
        "and I'll write again if it changes noticeably."
    ),
    "t_m_unsub": "🔕 You won't get the weekend forecast for this peak anymore",
    "t_m_sub_limit": "You can follow up to {n} peaks — unsubscribe from one first.",

    "btn_m_share": "📤 Share",
    "m_share_text": "⛰ {name} · {ele} m — summit weather, climbing windows and altitude profile",
    "t_m_shared_added": "⛰ Peak added from the link — it's now in your peaks",

    "btn_sos": "🆘 SOS and coordinates",
    "btn_sos_share": "📤 Send coordinates",
    "sos_title": "🆘 <b>Emergency help</b>",
    "sos_numbers": (
        "📞 <b>112</b> — single emergency number\n"
        "🇺🇿 Uzbekistan: <b>101</b> — fire and rescue · <b>103</b> — ambulance · <b>102</b> — police"
    ),
    "sos_no_point": (
        "📍 No exact coordinates yet. Send your location with the button below — "
        "I'll show them in the formats rescuers use."
    ),
    "sos_point": "📍 <b>Your coordinates</b> · {when}",
    "sos_now": "just now",
    "sos_min_ago": "{n} min ago",
    "sos_h_ago": "{h} h {m} min ago",
    "sos_ele": "⛰ Elevation ≈ {ele} m",
    "sos_place": "🏘 Near: {place}",
    "sos_map": "🗺 <a href=\"{url}\">Open on the map</a>",
    "sos_tell": (
        "<b>What to tell rescuers</b>\n"
        "1. Where you are — read out the coordinates\n"
        "2. What happened and how many are injured\n"
        "3. How many of you there are, and whether you have warm clothes, water and light\n"
        "4. Your phone number — keep the phone on"
    ),
    "sos_wait": (
        "<b>While you wait</b>\n"
        "• Stay where you are if it's safe — you'll be found faster\n"
        "• Keep warm, shelter from the wind, stay together\n"
        "• Save battery: minimum brightness, turn off what you don't need\n"
        "• Signal with a light at night and with bright clothing by day"
    ),
    "sos_hint": "⌨️ The «Send my location» button below the input field updates the coordinates 👇",
    "sos_share": "🆘 My coordinates: {lat}, {lon}",
    "sos_share_ele": ", elevation ≈ {ele} m",
    "cmd_sos": "🆘 SOS: coordinates and emergency numbers",

    "a_stats": (
        "📊 <b>Statistics</b>\n\n"
        "👥 Users: <b>{users}</b> (+{new_7d} in 7 days)\n"
        "🟢 Active: {active_1d} in a day · {active_7d} in 7 days · {active_30d} in 30 days\n"
        "📍 With a place: {with_place} · 🔔 get the daily summary: {notify}\n"
        "🌐 Languages: ru {lang_ru} · uz {lang_uz} · en {lang_en}\n\n"
        "⛰ Private peaks: {peaks} of {peak_owners} users\n"
        "🏔 In the catalog: {catalog}, from users {community} · ⏳ pending: {pending}\n"
        "🔔 Weekend forecast subscriptions: {subs} of {subscribers} users\n"
        "🧗 On a route in the last day: {on_route_1d}\n"
        "⏱ Trips in 7 days: {trips_7d} · on a route now: {trips_active} · trusted contacts: {contacts}"
    ),
})


# ── check-in deadline and trusted contacts ──
STRINGS.update({
    "m_live_hint": (
        "📡 You can turn on live sharing: 📎 → Location → <b>«Share My Live Location»</b>. "
        "The point will then update by itself — for SOS and the check-in deadline."
    ),
    "trip_title": "⏱ <b>Check-in deadline</b> · {name}",
    "trip_intro": (
        "Set when you'll be back. If you don't tap «✅ I'm back», I'll remind you first, and 30 minutes later "
        "I'll tell your trusted contacts where you went and send your last point from the route."
    ),
    "trip_contacts": "👥 Trusted contacts: {names}",
    "trip_no_contacts": "👥 No trusted contacts yet — without them I can only remind you. Add one below.",
    "trip_sunset": "🌅 Sunset today at {time}",
    "trip_pick": "In how many hours will you be back? 👇\n<i>Or type the return time, e.g. 18:30</i>",
    "trip_active_title": "⏱ <b>You're on a route</b> · {name}",
    "trip_started": "🚶 Started at {time}",
    "trip_deadline": "🏁 Back by <b>{time}</b> · {left} left",
    "trip_overdue": "⏰ The <b>{time}</b> deadline passed {late} ago",
    "trip_no_point": "📍 No point from the route yet — send your location in «🧗 I'm on the route».",
    "trip_point": "📍 Last point: {time} ({ago})",
    "trip_point_ele": " · ≈ {ele} m",
    "trip_alerted_note": "🚨 Your contacts have been alerted — check in as soon as you're safe.",
    "trip_live_hint": "<i>Tip: turn on live location in «🧗 I'm on the route» — the point will update by itself.</i>",
    "trip_reminder": (
        "⏰ <b>The check-in deadline has passed</b>\n\n"
        "The return from «{name}» was planned by {time}. Is everything OK?\n\n"
        "If you don't check in within 30 minutes, your trusted contacts will be alerted."
    ),
    "trip_alarm_title": "🚨 <b>No check-in: {who}</b>",
    "trip_alarm_body": (
        "⛰ Route: «{name}» ({ele} m)\n"
        "🚶 Started: {date}, {start}\n"
        "🏁 Deadline: <b>{deadline}</b> — passed, no «I'm back» check-in\n"
        "👤 Profile: {who}"
    ),
    "trip_alarm_todo": (
        "<b>What to do</b>\n"
        "1. Try to get in touch: call or message {who}.\n"
        "2. No luck — call <b>112</b> and give them the route, start time and last point.\n"
        "I'll let you know as soon as there's a check-in."
    ),
    "trip_owner_alerted": (
        "🚨 <b>The check-in deadline passed 30 minutes ago</b>\n\n"
        "Your trusted contacts have been alerted: {names}.\n"
        "As soon as you're safe, tap «✅ I'm back» — they'll get an all-clear."
    ),
    "trip_back_notice": "✅ <b>All clear:</b> {who} checked in back from «{name}», everything is fine.",
    "trip_extended_notice": "🔄 {who} is in touch and extends the check-in deadline to {time}.",
    "contacts_title": "👥 <b>Trusted contacts</b>",
    "contacts_intro": (
        "If you're not back from a route by the deadline, I'll send them where you went and your last point. "
        "Invite someone with the button below: they open the link in Telegram and confirm. Up to 5 contacts."
    ),
    "contacts_list": "Now: {names}\n<i>Tap a name to remove the contact.</i>",
    "contacts_empty": "Nobody yet.",
    "invite_text": (
        "👥 <b>{who}</b> asks you to be a trusted contact for hikes.\n\n"
        "If {who} isn't back from a route by the deadline, I'll send you where they went and their last point. "
        "Nothing else: no location at other times, no newsletters."
    ),
    "invite_share": (
        "Be my trusted contact for hikes: if I'm not back from a route on time, "
        "the AiroPost bot will tell you where to look for me."
    ),
    "invite_done": "✅ Done! You're a trusted contact for {who}. If something goes wrong, I'll write.",
    "invite_own": "🔗 This is your own link — send it to a friend or relative.",
    "contact_added_notice": "👥 {who} is now your trusted contact.",
    "btn_trip": "⏱ Check-in deadline",
    "btn_trip_active": "⏱ On a route: {name}",
    "btn_trip_contacts": "👥 Trusted contacts ({n})",
    "btn_trip_contacts_short": "👥 Contacts",
    "btn_trip_done": "✅ I'm back",
    "btn_trip_extend": "🔄 +{h} h",
    "btn_trip_cancel": "❌ Cancel the trip",
    "btn_invite": "➕ Invite a contact",
    "btn_invite_yes": "✅ I agree",
    "btn_invite_no": "Decline",
    "t_trip_started": "⏱ Trip started — be back by {time}",
    "t_trip_done": "✅ Welcome back!",
    "t_trip_extended": "🔄 Deadline extended to {time}",
    "t_trip_cancelled": "Trip cancelled",
    "t_contact_removed": "Contact removed",
    "t_contacts_limit": "This person already has {n} trusted contacts — no more can be added.",
    "t_invite_stale": "The invitation is outdated — ask for a new link.",
})

# ── снег и лавинная опасность ──
STRINGS.update({
    "av_snow": "❄️ Fresh snow on the summit over 3 days: ≈ {recent} cm",
    "av_snow_coming": ", another ≈ {coming} cm expected in 24 h",
    "av_level": "{icon} Avalanche danger from the weather: <b>{level}</b> — {reasons}",
    "av_levels": ["elevated", "high", "very high"],
    "av_some": "fresh snow",
    "av_fresh": "lots of fresh snow",
    "av_lot": "heavy snowfall",
    "av_wind": "wind during snowfall — wind slabs",
    "av_warm": "warming above the summit",
    "av_rain": "rain on fresh snow",
    "av_note": "<i>This is an estimate from the weather, not an official avalanche forecast. Slopes steeper than 30° are dangerous after snowfall.</i>",
    "gn_avalanche": "🏔 Avalanche danger: stay on ridges and gentle slopes, avoid gullies; everyone carries avalanche gear.",
})

# ── перевалы и горнолыжка ──
STRINGS.update({
    'btn_passes': '🛣 Passes',
    'btn_passes_back': '⬅️ To passes',
    'btn_ski': '⛷ Ski resorts',
    'btn_ski_back': '⬅️ To resorts',
    'btn_ski_sub': '🔔 Notify me about fresh snow',
    'btn_ski_unsub': '🔕 Stop fresh snow alerts',
    'road_title': '🛣 <b>Mountain passes and roads</b>',
    'road_intro': '<i>Weather at pass height — where the road is, not down in the valley.</i>',
    'road_na': 'forecast unavailable',
    'road_note': '<i>Pass closures are announced by the traffic police and emergency service — check official news before the trip.</i>',
    'road_clear': 'dry, no precipitation',
    'road_by': '{what} by {time}',
    'road_now': '<b>Now</b> · {time}',
    'road_next': '<b>Next 24 hours</b>',
    'road_days': '<b>By day</b>',
    'road_snow': 'snowfall',
    'road_ice': 'black ice',
    'road_rain': 'rain',
    'road_fog': 'fog',
    'road_wind': 'strong wind',
    'ski_title': '⛷ <b>Ski resorts</b>',
    'ski_intro': '<i>Snow and weather at the top of the slopes — modelled at the upper station height.</i>',
    'ski_snow': '❄️ Fresh snow at the top: {day} cm in 24 h, {three} cm in 3 days',
    'ski_coming': ', {cm} cm more expected',
    'ski_temp': '🌡 Top {top}, base {base} · 💨 {wind} m/s',
    'ski_powder': "🎉 Fresh snow — it's a powder day!",
    'ski_lifts': '💨 Strong wind at the top — lifts may be stopped',
    'ski_days': '<b>Ski days</b> <i>(09–17)</i>',
    'ski_d_temp': 'top {lo}…{hi}',
    'ski_d_snow': '❄️ snow {cm} cm',
    'ski_d_wind': '💨 wind up to {v} m/s',
    'ski_d_fog': '🌫 fog at the top',
    'ski_d_slush': 'slushy at the base',
    'ski_d_rain': '🌧 rain at the base',
    'ski_sub_on': "🔔 I'll write in the morning when 10 cm or more of fresh snow falls.",
    'ski_sub_off': "<i>Subscribe and I'll write in the morning when 10 cm or more of fresh snow falls.</i>",
    'ski_note': '<i>Slope heights are approximate; check lift operation with the resort.</i>',
    'ski_alert': '🎉 <b>{name}: {cm} cm of fresh snow!</b>',
    't_ski_sub': "🔔 I'll write in the morning when the resort gets 10 cm or more of fresh snow",
    't_ski_unsub': '🔕 Snow alerts are off',
})
