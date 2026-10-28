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
    "coords_hint": "🧭 Yoki koordinatalarni matn bilan: <code>41.49519, 70.058671</code> — xaritadan nusxalash mumkin.",
    "coords_error": "❗️ Koordinatalarni tushunmadim. Misol: <code>41.49519, 70.058671</code>\n",
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

# ── togʻlar ──
STRINGS.update({
    "m_title": "⛰ <b>Togʻlar</b>",
    "m_intro": (
        "Choʻqqilar uchun prognoz: turli balandlikdagi harorat va shamol, nol izoterma, "
        "yogʻingarchilik, momaqaldiroq va chiqish uchun eng qulay kunlar."
    ),
    "m_empty": "Hozircha saqlangan choʻqqilar yoʻq. Birinchisini qoʻshing 👇",
    "m_saved": "Saqlangan choʻqqilar:",
    "m_add_prompt": (
        "⛰ <b>Yangi choʻqqi</b>\n\n"
        "Choʻqqi yoki dovon nomini yozing, masalan: <i>Katta Chimyon</i>, "
        "<i>Qizilnura</i>, <i>Lenin choʻqqisi</i>.\n\n"
        "Yoki xaritadagi nuqtani yuboring: 📎 → <b>Joylashuv</b> → belgini choʻqqiga suring → "
        "<b>«Tanlangan joylashuvni yuborish»</b>."
    ),
    "m_searching": "🔎 «{q}» choʻqqisi qidirilmoqda…",
    "m_results": "🔎 «{q}» boʻyicha topildi. Choʻqqini tanlang 👇",
    "m_not_found": (
        "😕 «{q}» choʻqqisi topilmadi.\n\n"
        "Boshqacha yozib koʻring (Big Chimgan, Большой Чимган) yoki xaritadagi nuqtani yuboring."
    ),
    "m_point_name": "Nuqta {lat}, {lon}",
    "m_snapped": "📍 Belgi OpenStreetMap’dagi eng yaqin choʻqqiga bogʻlandi — nomi va balandligi oʻsha yerdan.",
    "m_pin_hint": (
        "ℹ️ {ele} m balandlik relyef xaritasidan olindi — oʻtkir choʻqqilarda u pastroq chiqishi mumkin. "
        "Aniqlashtirish yoki nomini oʻzgartirish: ✏️ Oʻzgartirish."
    ),
    "m": "m",
    "m_now": "<b>Hozir choʻqqida</b> · {time}",
    "m_temp": "🌡 <b>{t}</b> · his qilinishi {feels}",
    "m_wind": "💨 Shamol <b>{v} m/s</b> {dir} {arrow}",
    "m_in_cloud": "🌫 Choʻqqi bulut ichida — koʻrinish yomon",
    "m_precip": "{icon} {phase} {mm} mm/soat · ehtimoli {p}%",
    "m_no_precip": "☀️ Yogʻingarchiliksiz · ehtimoli {p}%",
    "m_snow": "qor",
    "m_sleet": "hoʻl qor",
    "m_rain": "yomgʻir",
    "m_fl": "🧊 Nol izoterma: <b>{h} m</b>",
    "m_fl_below": " — choʻqqida sovuq",
    "m_fl_above": " — choʻqqidan yuqorida",
    "m_storm": "⚡️ Momaqaldiroq xavfi: {level}",
    "m_storm_levels": ["past", "oʻrtacha", "yuqori"],
    "m_thunder_now": "⛈ <b>Momaqaldiroq!</b>",
    "m_uv": "🔆 Kunduzi UB {uv} gacha (balandlik hisobga olingan) — koʻzoynak va krem shart",
    "m_sun": "🌅 Quyosh chiqishi {rise} · botishi {set}",
    "m_windows": "<b>Chiqish uchun qulay kunlar</b>",
    "m_good": "qulay",
    "m_caution": "ehtiyotkorlik bilan",
    "m_bad": "tavsiya etilmaydi",
    "r_thunder": "momaqaldiroq",
    "r_storm_risk": "momaqaldiroq xavfi",
    "r_wind": "shamol {v} m/s gacha",
    "r_precip": "{phase} {mm} mm",
    "r_prob": "yogʻingarchilik {p}%",
    "r_cold": "his qilinishi {t} gacha",
    "r_cloud": "{h} soat bulut ichida",
    "m_updated": "<i>Maʼlumotlar {time} holatiga. Model prognozi {ele} m balandlik uchun.</i>",
    "m_profile_title": "📊 <b>Balandlik profili</b> · {name}",
    "m_profile_legend": "<i>balandlik · harorat (his qilinishi) · shamol · yogʻin</i>",
    "m_fl_row": "── 🧊 0° — {h} m ──",
    "m_you": " (siz)",
    "m_profile_note": (
        "<i>Model boʻyicha erkin atmosfera harorati. Kunduzi quyoshli yonbagʻirlarda issiqroq, "
        "kechasi vodiylarda sovuqroq boʻlishi mumkin.</i>"
    ),
    "m_hourly_title": "🕐 <b>Choʻqqi soatma-soat</b> · {name} ({ele} m)",
    "m_hourly_legend": "<i>harorat (his qilinishi) · shamol · yogʻin</i>",
    "m_outlook_title": "📅 <b>Chiqish uchun kunlar</b> · {name}",
    "m_outlook_day": "🌡 {tmin}…{tmax} (his qilinishi {feels} gacha) · 💨 {wind} m/s gacha",
    "m_outlook_fl": " · 🧊 0° {lo}–{hi} m",
    "m_outlook_note": "<i>Baho choʻqqi balandligida kunduzgi 06–18 soatlar boʻyicha.</i>",
    "m_precip_none": "☀️ yogʻingarchiliksiz",
    "m_route_prompt": (
        "🧗 <b>Men yoʻldaman</b> · {name}\n\n"
        "Pastdagi tugma orqali joylashuvingizni yuboring — shu yerdagi, choʻqqidagi "
        "va oradagi balandliklardagi ob-havoni koʻrsataman.\n\n"
        "<i>Kuchsiz internet ham yetadi: javob — bitta qisqa xabar.</i>"
    ),
    "m_route_hint": "⌨️ «Joylashuvni yuborish» tugmasi — kiritish maydoni ostida 👇",
    "m_route_title": "🧗 <b>Yoʻlda</b> · {name}",
    "m_route_you": "📍 Siz: <b>{ele} m</b> · choʻqqigacha {km} km va {climb} m",
    "m_route_top": "📍 Siz choʻqqi yonidasiz: <b>{ele} m</b>",
    "m_route_sun": "🕐 {time} · quyosh botishi {set}, yorugʻ vaqt {left} qoldi",
    "m_route_dark": "🌙 {time} · qorongʻi, quyosh {rise} da chiqadi",
    "m_here": "<b>Shu yerda:</b> {icon} {t}, his qilinishi {feels}, shamol {v} m/s",
    "m_summit_short": "<b>Choʻqqida:</b> {t}, his qilinishi {feels}, shamol {v} m/s",
    "m_way_up": "<b>Yuqoriga yoʻlda</b>",
    "m_next_hours": "<b>Choʻqqi yaqin soatlarda</b>",
    "m_warnings": "<b>⚠️ Diqqat</b>",
    "w_dark": "quyosh botishiga {h} soatdan kam qoldi — tushishni rejalashtiring",
    "w_wind": "choʻqqida shamol {time} ga {v} m/s gacha kuchayadi",
    "w_storm": "{time} ga momaqaldiroq xavfi",
    "w_precip": "{time} ga choʻqqida {phase}",
    "w_cold": "choʻqqida his qilinishi {t} gacha",
    "w_cloud": "{time} ga choʻqqi bulut ichida qoladi",
    "m_all_good": "✅ Yaqin soatlarda choʻqqida ob-havo barqaror",
    "m_offline_header": (
        "📥 <b>Oflayn prognoz</b> · {name} ({ele} m)\n"
        "<i>{date}, {time} da saqlandi. Bot bu xabarni oʻchirmaydi.</i>"
    ),
    "m_ele_prompt": (
        "✏️ <b>{name}</b> · {ele} m\n\n"
        "Aniq balandlikni raqam bilan yuboring, masalan <i>3309</i>, yoki yangi nomni matn bilan."
    ),
    "m_ele_error": "❗️ Balandlik 100 dan 8900 m gacha raqam boʻlishi kerak.\n",
    "m_delete_confirm": "🗑 <b>{name}</b> choʻqqisini oʻchirasizmi?",

    "btn_mountains": "⛰ Togʻlar",
    "btn_m_add": "➕ Choʻqqi qoʻshish",
    "btn_m_profile": "📊 Balandlik profili",
    "btn_m_hourly": "🕐 Soatma-soat",
    "btn_m_outlook": "📅 7 kunlik oynalar",
    "btn_m_route": "🧗 Men yoʻldaman",
    "btn_m_offline": "📥 Oflayn saqlash",
    "btn_m_ele": "✏️ Oʻzgartirish",
    "btn_m_delete": "🗑 Oʻchirish",
    "btn_m_back": "⬅️ Choʻqqilarga",
    "btn_m_to_peak": "⬅️ Choʻqqiga",
    "btn_m_yes_delete": "🗑 Ha, oʻchirish",
    "btn_m_route_again": "📍 Nuqtani yangilash",
    "btn_m_minus": "◀️ −3 soat",
    "btn_m_plus": "+3 soat ▶️",
    "btn_m_now": "🕐 Hozir",

    "t_m_limit": "Koʻpi bilan {n} ta choʻqqi saqlash mumkin — keraksizini oʻchiring.",
    "t_m_added": "⛰ Choʻqqi qoʻshildi",
    "t_m_saved": "📥 Prognoz chatga saqlandi — internetsiz ham koʻrinadi",
    "t_m_ele": "✅ Balandlik: {ele} m",
    "t_m_renamed": "✅ Nomi oʻzgartirildi",
    "t_m_deleted": "🗑 Choʻqqi oʻchirildi",
    "t_m_missing": "Choʻqqi topilmadi — roʻyxatni qaytadan oching.",
})

# ── choʻqqilar katalogi va moderatsiya ──
STRINGS.update({
    "m_private_note": "🔒 Choʻqqilaringizni faqat siz koʻrasiz.",
    "m_catalog_btn": "🏔 Oʻzbekiston choʻqqilari ({n})",
    "m_catalog_title": "🏔 <b>Oʻzbekiston choʻqqilari</b>",
    "m_catalog_intro": (
        "Sayohat va choʻqqiga chiqish uchun asosiy choʻqqilar — hamma uchun ochiq. "
        "Oʻz choʻqqingizni uning sahifasidagi 📢 tugmasi orqali katalogga taklif qilishingiz mumkin."
    ),
    "m_catalog_page": "<i>{n} sahifadan {p}-sahifa</i>",
    "region_tashkent": "Toshkent viloyati",
    "region_jizzakh": "Jizzax viloyati",
    "region_surkhandarya": "Surxondaryo viloyati",
    "region_community": "Foydalanuvchilar qoʻshgan",
    "st_private": "🔒 Faqat siz koʻrasiz",
    "st_pending": "⏳ Administrator tekshiruvida",
    "st_approved": "✅ Katalogda eʼlon qilingan",
    "st_rejected": "❌ Eʼlon qilish rad etildi — qayta yuborish mumkin",
    "st_catalog": "🏔 Oʻzbekiston choʻqqilari katalogi",
    "st_community": "🏔 Katalog · foydalanuvchi taklif qilgan",
    "m_publish_confirm": (
        "📢 <b>«{name}» eʼlon qilinsinmi?</b>\n\n"
        "⛰ {ele} m · 📍 <code>{lat}, {lon}</code>\n\n"
        "Choʻqqini administrator tekshiradi. Tasdiqlangach, u «Oʻzbekiston choʻqqilari» "
        "katalogida paydo boʻladi va uni botning barcha foydalanuvchilari koʻradi."
    ),
    "m_published_notice": (
        "✅ <b>«{name}» choʻqqingiz eʼlon qilindi!</b>\n"
        "Endi uni «Oʻzbekiston choʻqqilari» katalogida hamma koʻradi."
    ),
    "m_rejected_notice": (
        "❌ <b>«{name}» choʻqqisini eʼlon qilish rad etildi.</b>\n"
        "Choʻqqi sizning roʻyxatingizda qoldi — uni faqat siz koʻrasiz."
    ),
    "btn_m_publish": "📢 Eʼlon qilish",
    "btn_m_publish_yes": "✅ Tekshiruvga yuborish",
    "btn_m_catalog_back": "⬅️ Katalogga",
    "t_m_sent": "⏳ Administrator tekshiruviga yuborildi",
    "t_m_duplicate": "Bu choʻqqi katalogda yoki tekshiruvda bor: {name}",
    "t_m_pending": "Ariza allaqachon tekshiruvda",
    "t_m_no_admin": "Administrator bilan bogʻlanib boʻlmadi — keyinroq urinib koʻring",
    "t_m_readonly": "Bu umumiy katalogdagi choʻqqi — uni oʻzgartirib boʻlmaydi",

    "a_request": (
        "📢 <b>Eʼlon qilish uchun ariza #{id}</b>\n\n"
        "⛰ <b>{name}</b> · {ele} m\n"
        "📍 <code>{lat}, {lon}</code>\n"
        "🗺 <a href=\"{map}\">Xaritada ochish</a>\n"
        "👤 {author}"
    ),
    "a_approved": "✅ <b>Eʼlon qilindi</b> — {admin}",
    "a_rejected": "❌ <b>Rad etildi</b> — {admin}",
    "a_no_pending": "📭 Tekshiruvdagi arizalar yoʻq.",
    "btn_a_approve": "✅ Eʼlon qilish",
    "btn_a_reject": "❌ Rad etish",
    "t_a_done": "Ariza allaqachon koʻrib chiqilgan",
    "t_a_forbidden": "Faqat administrator uchun",
    "t_a_approved": "✅ Eʼlon qilindi",
    "t_a_rejected": "❌ Rad etildi",
})
