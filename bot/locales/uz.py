STRINGS = {
    "lang_name": "🇺🇿 Oʻzbekcha",
    "decimal": ",",

    # ── sanalar ──
    "weekdays": ["Du", "Se", "Cho", "Pa", "Ju", "Sha", "Ya"],
    "months": ["yan", "fev", "mar", "apr", "may", "iyn", "iyl", "avg", "sen", "okt", "noy", "dek"],
    "date": "{wd}, {d}-{m}",
    "day_month": "{d}-{m}",
    "today": "Bugun",
    "tomorrow": "Ertaga",

    # ── ob-havo ──
    "wmo": {
        0: "Ochiq havo", 1: "Asosan ochiq", 2: "Qisman bulutli", 3: "Bulutli",
        45: "Tuman", 48: "Qirovli tuman",
        51: "Kuchsiz shivalama", 53: "Shivalama", 55: "Kuchli shivalama",
        56: "Muzli shivalama", 57: "Kuchli muzli shivalama",
        61: "Kuchsiz yomgʻir", 63: "Yomgʻir", 65: "Kuchli yomgʻir",
        66: "Muzli yomgʻir", 67: "Kuchli muzli yomgʻir",
        71: "Kuchsiz qor", 73: "Qor", 75: "Kuchli qor", 77: "Qor donachalari",
        80: "Kuchsiz jala", 81: "Jala", 82: "Kuchli jala",
        85: "Kuchsiz qor boʻroni", 86: "Kuchli qor boʻroni",
        95: "Momaqaldiroq", 96: "Doʻl bilan momaqaldiroq", 99: "Kuchli doʻl bilan momaqaldiroq",
    },
    "directions": [
        "shimoliy", "shimoli-sharqiy", "sharqiy", "janubi-sharqiy",
        "janubiy", "janubi-gʻarbiy", "gʻarbiy", "shimoli-gʻarbiy",
    ],
    "beaufort": [
        "sokin", "juda kuchsiz", "kuchsiz", "yengil", "moʻtadil", "sezilarli", "kuchli",
        "juda kuchli", "oʻta kuchli", "boʻron", "kuchli boʻron", "shiddatli boʻron", "dovul",
    ],
    "uv_levels": ["past", "oʻrtacha", "yuqori", "juda yuqori", "ekstremal"],
    "periods": {3: "Tun", 9: "Ertalab", 15: "Kunduz", 21: "Kechqurun"},

    # ── birliklar ──
    "ms": "m/s",
    "mm": "mm",
    "km": "km",
    "m": "m",
    "ug": "mkg/m³",
    "pressure": "{mm} mm sim. ust. ({hpa} gPa)",
    "duration": "{h} soat {m:02d} daq",

    # ── havo sifati: nomi, maslahat, sport, derazalar, niqob, tozalagich ──
    "aqi_levels": [
        ("yaxshi", "Havo toza — sayr qilish va xonani shamollatish uchun ajoyib vaqt.",
         "mumkin", "oching", "kerak emas", "kerak emas"),
        ("oʻrtacha", "Havo sifati maqbul. Juda taʼsirchan odamlarga tashqarida uzoq zoʻriqmaslik tavsiya etiladi.",
         "mumkin", "ochsa boʻladi", "kerak emas", "ixtiyoriy"),
        ("taʼsirchan guruhlar uchun zararli",
         "Bolalar, keksalar, astma yoki yurak kasalligi bor odamlar tashqarida kamroq boʻlgani maʼqul.",
         "kamaytiring", "yoping", "taʼsirchanlarga — ha", "yoqing"),
        ("zararli", "Tashqarida boʻlish vaqtini cheklang va ochiq havoda mashq qilmang.",
         "tavsiya etilmaydi", "yoping", "taqing", "yoqing"),
        ("juda zararli", "Hamma uchun jiddiy xavf. Xonada qoling.",
         "tavsiya etilmaydi", "yoping", "majburiy", "yoqing"),
        ("xavfli", "Favqulodda ifloslanish. Zarurat boʻlmasa tashqariga chiqmang.",
         "tavsiya etilmaydi", "yoping", "majburiy (N95/FFP2)", "maksimal quvvatda"),
    ],
    "eu_aqi_levels": ["yaxshi", "qoniqarli", "oʻrtacha", "yomon", "juda yomon", "oʻta yomon"],
    "pollutants": {
        "pm2_5": "mayda zarrachalar", "pm10": "yirik zarrachalar", "ozone": "ozon",
        "nitrogen_dioxide": "azot dioksidi", "sulphur_dioxide": "oltingugurt dioksidi",
        "carbon_monoxide": "is gazi", "dust": "",
    },
    "dust": "Chang",

    # ── boʻlaklar ──
    "calm": "sokin",
    "gusts": "zarbalari {g} m/s gacha",
    "uv_now_max": "hozir {now}, maks. {max} ({level})",
    "precip_sum": "yogʻingarchilik {mm} mm",
    "precip_chance": "yogʻingarchilik ehtimoli {p}%",
    "no_precip": "yogʻingarchiliksiz",
    "my_place": "Mening joyim",

    # ── salomlashish va xulosa ──
    "welcome": (
        "👋 <b>Salom, {name}!</b>\n\n"
        "Men <b>AiroPost</b> — ob-havo va havo sifati botiman.\n\n"
        "Har kuni qulay vaqtda xulosa yuboraman:\n"
        "🌡 harorat va «his qilinishi»\n"
        "💨 shamol, uning zarbalari va yoʻnalishi\n"
        "💧 namlik, bosim, bulutlilik, yogʻingarchilik\n"
        "🔆 UB-indeks, quyosh chiqishi va botishi\n"
        "🌫 havo sifati indeksi AQI va ifloslantiruvchi moddalar\n\n"
        "Boshlash uchun joyni tanlang 👇"
    ),
    "greet_morning": "🌅 <b>Xayrli tong!</b>",
    "greet_day": "☀️ <b>Xayrli kun!</b>",
    "greet_evening": "🌆 <b>Xayrli kech!</b>",
    "greet_night": "🌙 <b>Xayrli tun!</b>",
    "greet_suffix": "Ob-havo xulosangiz:",
    "saved": "✅ <b>Joy saqlandi!</b>",
    "saved_schedule": "Xulosa har kuni soat {time} da keladi.",

    # ── asosiy ekran ──
    "feels": "🤗 His qilinishi: {t}",
    "today_range": "🗓 Bugun {min} … {max}, {precip}",
    "wind_line": "💨 Shamol: {wind}",
    "humidity": "💧 Namlik: {h}% · shudring nuqtasi {dew}",
    "pressure_line": "🧭 Bosim: {p}",
    "clouds": "☁️ Bulutlilik: {c}%",
    "visibility": " · koʻrinish {v}",
    "uv_line": "🔆 UB-indeks: {uv}",
    "sun": "🌅 Quyosh chiqishi {rise} · botishi {set} · kun {len}",
    "next": "<b>Keyingi soatlar</b>",
    "air_unavailable": "🌫 Havo sifati maʼlumotlari vaqtincha mavjud emas",
    "air_short": "<b>Havo: AQI {aqi}</b> — {level}",
    "main_pollutant": "Asosiy ifloslantiruvchi: {p}",
    "schedule_on": "🔔 Xulosa har kuni soat {time} da",
    "schedule_off": "🔕 Kundalik xulosa oʻchirilgan",

    # ── prognozlar ──
    "hourly_title": "🕐 <b>Soatlik prognoz</b>",
    "hourly_legend": "<i>harorat (his qilinishi) · yogʻingarchilik · shamol</i>",
    "daily_title": "📅 <b>7 kunlik prognoz</b>",
    "daily_wind": "💨 {dir} {arrow} {max} m/s gacha, zarbalari {g} · 🔆 UB {uv}",

    # ── havo ──
    "air_title": "🌫 <b>Havo sifati</b>",
    "air_na": "Maʼlumotlar vaqtincha mavjud emas. Bir-ikki daqiqadan soʻng yangilab koʻring.",
    "aqi_line": "<b>AQI {aqi}</b> (US) — {level}",
    "eu_line": "🇪🇺 Yevropa indeksi: {v} — {level}",
    "source": "Manba: {s}",
    "pollutants_title": "<b>Ifloslantiruvchi moddalar</b> <i>(JSST kunlik meʼyoriga nisbatan ×)</i>",
    "advice_title": "<b>Tavsiyalar</b>",
    "sport": "🚴 Ochiq havoda sport: {v}",
    "windows": "🪟 Derazalar: {v}",
    "mask": "😷 Niqob: {v}",
    "purifier": "🌀 Havo tozalagich: {v}",
    "aqi_forecast": "<b>AQI prognozi</b> <i>(CAMS modeli)</i>",
    "scale": "<i>Shkala: 🟢 0–50 · 🟡 51–100 · 🟠 101–150 · 🔴 151–200 · 🟣 201–300 · 🟤 300+</i>",

    # ── sozlamalar ──
    "settings_title": "⚙️ <b>Sozlamalar</b>",
    "s_place": "📍 Joy: <b>{p}</b>",
    "s_place_none": "tanlanmagan",
    "s_time": "⏰ Xulosa vaqti: <b>{time}</b>",
    "s_notify": "🔔 Kundalik xulosa: <b>{state}</b>",
    "on": "yoqilgan",
    "off": "oʻchirilgan",
    "s_next": "📬 Keyingi xulosa: {when} soat {time} da",
    "today_l": "bugun",
    "tomorrow_l": "ertaga",
    "s_lang": "🌐 Til: {name}",
    "lang_title": "🌐 <b>Tilni tanlang</b>\nВыберите язык · Choose language",

    # ── vaqt ──
    "time_title": "⏰ <b>Kundalik xulosa vaqti</b>",
    "time_current": "Hozir: <b>{time}</b>",
    "time_local": " <i>(mahalliy, {tz})</i>",
    "pick_hour": "Soatni tanlang 👇",
    "time_hint": "<i>Yoki vaqtni xabar qilib yuboring, masalan 07:30</i>",
    "time_error": "❗️ Vaqtni tushunmadim. SS:DD formatida yozing, masalan 07:30\n",
    "time_hour": "Soat: <b>{h}</b>",
    "pick_minutes": "Endi daqiqani tanlang 👇",
    "time_saved": "✅ Xulosa soat <b>{time}</b> da keladi",

    # ── joy ──
    "location_prompt": (
        "📍 <b>Joyni tanlash</b>\n\n"
        "Shahar yoki aholi punkti nomini yozing,\n"
        "masalan: <i>Toshkent</i>, <i>Samarqand</i>, <i>Buxoro</i>.\n"
        "Davlatni ham koʻrsatish mumkin: <i>Buxoro, Oʻzbekiston</i>.\n\n"
        "Yoki kiritish maydoni ostidagi <b>«📍 Joylashuvni yuborish»</b> tugmasini bosing — "
        "prognoz aynan sizning joyingiz uchun boʻladi."
    ),
    "location_keyboard_hint": "⌨️ Joylashuv tugmasi — kiritish maydoni ostida 👇",
    "searching": "🔎 «{q}» qidirilmoqda…",
    "locating": "📡 Joy aniqlanmoqda…",
    "search_results": "🔎 «{q}» boʻyicha bir nechta joy topildi.\n\nKeraklisini tanlang 👇",
    "not_found": (
        "😕 «{q}» topilmadi.\n\n"
        "Yozilishini tekshiring yoki boshqa nom bilan urinib koʻring — masalan, eng yaqin yirik shahar. "
        "Joylashuvni yuborsangiz ham boʻladi."
    ),
    "error": (
        "⚠️ <b>Ob-havo maʼlumotlarini olib boʻlmadi</b>\n\n"
        "Ob-havo xizmati vaqtincha ishlamayapti. Bir daqiqadan soʻng urinib koʻring."
    ),

    # ── tugmalar ──
    "btn_pick_place": "📍 Joyni tanlash",
    "btn_change_place": "📍 Joyni oʻzgartirish",
    "btn_refresh": "🔄 Yangilash",
    "btn_hourly": "🕐 Soatlik",
    "btn_daily": "📅 7 kunlik",
    "btn_air": "🌫 Havo sifati",
    "btn_settings": "⚙️ Sozlamalar",
    "btn_back": "⬅️ Orqaga",
    "btn_cancel": "⬅️ Bekor qilish",
    "btn_earlier": "◀️ Oldinroq",
    "btn_later": "Keyinroq ▶️",
    "btn_time": "⏰ Xulosa vaqti: {time}",
    "btn_notify_off": "🔕 Xulosani oʻchirish",
    "btn_notify_on": "🔔 Xulosani yoqish",
    "btn_lang": "🌐 Til · Язык · Language",
    "btn_send_location": "📍 Joylashuvni yuborish",
    "btn_search_again": "📍 Qayta qidirish",
    "btn_retry": "🔄 Qayta urinish",
    "placeholder": "Shahar nomi…",

    # ── bildirishnomalar ──
    "t_refreshed": "🔄 Yangilandi",
    "t_on": "🔔 Xulosa yoqildi",
    "t_off": "🔕 Xulosa oʻchirildi",
    "t_saved": "✅ Joy saqlandi",
    "t_time": "✅ Xulosa soat {time} da keladi",
    "t_search_expired": "Qidiruv natijalari eskirdi — nomni qaytadan yuboring.",
    "t_stale": "Tugma eskirgan — /start yuboring",
    "t_lang": "✅ Oʻzbek tili",

    # ── buyruqlar ──
    "cmd_start": "🌤 Hozirgi ob-havo",
    "cmd_location": "📍 Joyni oʻzgartirish",
    "cmd_settings": "⚙️ Sozlamalar va xulosa vaqti",
    "cmd_language": "🌐 Til",
}
