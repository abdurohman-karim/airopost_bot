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
    "r_thunder": "momaqaldiroq {time} dan",
    "r_storm_risk": "momaqaldiroq xavfi {time} dan",
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


# ── yoʻl vaqti, nima olish kerak, dam olish kunlari, SOS, havolalar ──
STRINGS.update({
    "m_plan_up": "⏱ Koʻtarilish ≈ {d} → choʻqqida ≈ {at}",
    "m_plan_down": "↩️ Bu yerga tushish ≈ {d} → shu yerda ≈ {at}",
    "m_plan_latest": "🔙 Quyosh botguncha bu yerga tushish uchun choʻqqidan {time} dan kechiktirmay qayting",
    "m_plan_note": (
        "<i>Yoʻl vaqti oʻrtacha surʼat boʻyicha: soatiga 4 km va yuqoriga 400 m, dam olishlarsiz.</i>"
    ),
    "w_turnaround": "quyosh botguncha choʻqqiga chiqib qaytishga ulgurmaysiz — {time} dan kechiktirmay ortga qayting",
    "w_storm_before": "{time} ga momaqaldiroq — choʻqqiga yetib borishingizdan oldin (≈ {at})",
    "m_best": "🕐 eng yaxshisi {span}",

    "m_gear_title": "🎒 <b>Nima olish kerak</b> · {name}",
    "m_gear_summary": "Choʻqqida: 🌡 {tmin}…{tmax} (his qilinishi {feels} gacha) · 💨 {wind} m/s gacha",
    "m_gear_snow": "❄️ Soʻnggi 3 kunda choʻqqiga yoqqan yangi qor: ≈ {cm} sm",
    "m_gear_note": (
        "<i>{total} tadan {n} tasi yigʻildi. Narsalarni pastdagi tugmalar bilan belgilang. "
        "Roʻyxat choʻqqi balandligidagi prognoz boʻyicha tuzilgan.</i>"
    ),
    "g_water": "💧 Suv",
    "g_food": "🍫 Ovqat va yegulik",
    "g_headlamp": "🔦 Peshona chirogʻi",
    "g_power": "🔋 Powerbank",
    "g_firstaid": "🩹 Dori qutisi",
    "g_glasses": "🕶 Quyosh koʻzoynagi",
    "g_sunscreen": "🧴 SPF 50 krem",
    "g_cap": "🧢 Kepka yoki panama",
    "g_beanie": "🧣 Shapka va baf",
    "g_gloves": "🧤 Qoʻlqop",
    "g_fleece": "🧥 Flis",
    "g_down": "🪶 Pat kurtka",
    "g_mittens": "🥶 Issiq qoʻlqop va balaklava",
    "g_windproof": "🌬 Shamol kurtkasi",
    "g_rain": "☔️ Membrana yoki plashch",
    "g_drybag": "🎒 Germoqop",
    "g_crampons": "⛓ Koshka yoki mikroshiplar",
    "g_poles": "🦯 Trekking tayoqlari",
    "g_gaiters": "🥾 Getrlar",
    "g_axe": "⛏ Muz boltasi va kaska",
    "g_thermos": "♨️ Termos",
    "gr_water": "kishi boshiga kamida 2 l",
    "gr_water_hot": "issiq — kishi boshiga kamida 3 l",
    "gr_headlamp": "quyosh {time} da botadi; yorugʻda qaytishni rejalashtirsangiz ham oling",
    "gr_power": "oflayn prognozni ham oldindan saqlab qoʻying",
    "gr_poles": "tushishda tizzalarni asraydi",
    "gr_feels": "choʻqqida his qilinishi {t} gacha",
    "gr_wind": "shamol {v} m/s gacha",
    "gr_precip": "{phase} {mm} mm gacha",
    "gr_prob": "yogʻingarchilik ehtimoli {p}%",
    "gr_ice_snow": "choʻqqida sovuq va ≈ {cm} sm yangi qor — yonbagʻirlar muzlashi mumkin",
    "gr_ice_winter": "qish: nol izotermadan yuqorida qor va muz",
    "gr_snow": "soʻqmoqda qor",
    "gr_axe": "3500 m dan yuqorida tik qorli yonbagʻirlar",
    "gr_uv": "choʻqqida UB {uv} gacha",
    "gr_glare": "qor koʻzni qamashtiradi — 3–4 toifa kerak",
    "gr_sun": "yoʻlda quyosh va issiq",
    "gn_bad": "❌ Bu kun chiqish uchun tavsiya etilmaydi — boshqa sanani tanlagan maʼqul.",
    "gn_storm": "⛈ Momaqaldiroq {time} dan: erta yoʻlga chiqing va u boshlanguncha qir va choʻqqidan tushing.",
    "gn_best": "🕐 Choʻqqida eng sokin soatlar: {span}",
    "gn_altitude": (
        "🏔 3000 m dan yuqorida togʻ kasalligi boʻlishi mumkin: balandlikni shoshilmasdan oling va koʻproq "
        "suv iching. Kuchli bosh ogʻrigʻi, koʻngil aynishi, tinch holatda nafas qisishi — darhol pastga tushing."
    ),
    "btn_m_gear": "🎒 Nima olish kerak",

    "btn_m_weekend": "🗓 Dam olish kunlari qayerga",
    "m_weekend_title": "🗓 <b>Dam olish kunlari qayerga</b> · {days}",
    "m_weekend_intro": (
        "<i>Katalogdagi va sizning choʻqqilaringiz — eng yaxshilari tepada. "
        "Baho choʻqqi balandligida kunduzgi 06–18 soatlar boʻyicha.</i>"
    ),
    "m_weekend_empty": "😕 Choʻqqilar uchun prognoz hozircha mavjud emas. Bir-ikki daqiqadan soʻng urinib koʻring.",
    "m_weekend_loading": "🔎 Choʻqqilardagi ob-havo hisoblanmoqda…",
    "m_digest_header": "🔔 <b>Dam olish kunlari uchun prognoz</b> · {days}",
    "m_digest_note": (
        "<i>Prognoz sezilarli oʻzgarsa, xabar beraman. Obunani bekor qilish — choʻqqi sahifasidagi 🔕 tugmasi.</i>"
    ),
    "m_change_header": "🔔 <b>Dam olish kunlari prognozi oʻzgardi</b>",
    "btn_m_sub": "🔔 Dam olish kunlari prognozini yuborish",
    "btn_m_unsub": "🔕 Dam olish kunlari prognozini yubormaslik",
    "t_m_sub": (
        "🔔 Tayyor! Bu choʻqqi uchun dam olish kunlari prognozi payshanba kechqurun keladi, "
        "sezilarli oʻzgarsa — yana yozaman."
    ),
    "t_m_unsub": "🔕 Dam olish kunlari prognozi endi kelmaydi",
    "t_m_sub_limit": "Koʻpi bilan {n} ta choʻqqiga obuna boʻlish mumkin — keraksizidan obunani bekor qiling.",

    "btn_m_share": "📤 Ulashish",
    "m_share_text": "⛰ {name} · {ele} m — choʻqqidagi ob-havo, chiqish uchun qulay kunlar va balandlik profili",
    "t_m_shared_added": "⛰ Choʻqqi havola orqali qoʻshildi — endi u sizning roʻyxatingizda",

    "btn_sos": "🆘 SOS va koordinatalar",
    "btn_sos_share": "📤 Koordinatalarni yuborish",
    "sos_title": "🆘 <b>Favqulodda yordam</b>",
    "sos_numbers": (
        "📞 <b>112</b> — favqulodda xizmatlarning yagona raqami\n"
        "🇺🇿 Oʻzbekiston: <b>101</b> — FVV yongʻin va qutqaruv xizmati · <b>103</b> — tez yordam · "
        "<b>102</b> — politsiya"
    ),
    "sos_no_point": (
        "📍 Aniq koordinatalar hali yoʻq. Pastdagi tugma orqali joylashuvni yuboring — "
        "ularni qutqaruvchilar uchun qulay shaklda koʻrsataman."
    ),
    "sos_point": "📍 <b>Sizning koordinatalaringiz</b> · {when}",
    "sos_now": "hozirgina",
    "sos_min_ago": "{n} daqiqa oldin",
    "sos_h_ago": "{h} soat {m} daqiqa oldin",
    "sos_ele": "⛰ Balandlik ≈ {ele} m",
    "sos_place": "🏘 Yaqinida: {place}",
    "sos_map": "🗺 <a href=\"{url}\">Xaritada ochish</a>",
    "sos_tell": (
        "<b>Qutqaruvchilarga nima deyish kerak</b>\n"
        "1. Qayerdasiz — koordinatalarni ayting\n"
        "2. Nima boʻldi va nechta jabrlanuvchi bor\n"
        "3. Necha kishisiz, issiq kiyim, suv va chiroq bormi\n"
        "4. Telefon raqamingiz — telefonni yoqiq tuting"
    ),
    "sos_wait": (
        "<b>Yordamni kutayotganda</b>\n"
        "• Joy xavfsiz boʻlsa, uni tark etmang — sizni tezroq topishadi\n"
        "• Isining, shamoldan panalaning, birga turing\n"
        "• Quvvatni tejang: yorqinlikni minimumga tushiring, keraksizini oʻchiring\n"
        "• Kechasi chiroq bilan, kunduzi yorqin kiyim bilan signal bering"
    ),
    "sos_hint": "⌨️ Kiritish maydoni ostidagi «Joylashuvni yuborish» tugmasi koordinatalarni yangilaydi 👇",
    "sos_share": "🆘 Mening koordinatalarim: {lat}, {lon}",
    "sos_share_ele": ", balandlik ≈ {ele} m",
    "cmd_sos": "🆘 SOS: koordinatalar va favqulodda raqamlar",

    "a_stats": (
        "📊 <b>Statistika</b>\n\n"
        "👥 Foydalanuvchilar: <b>{users}</b> (7 kunda +{new_7d})\n"
        "🟢 Faol: sutkada {active_1d} · 7 kunda {active_7d} · 30 kunda {active_30d}\n"
        "📍 Joy tanlagan: {with_place} · 🔔 xulosa oladi: {notify}\n"
        "🌐 Tillar: ru {lang_ru} · uz {lang_uz} · en {lang_en}\n\n"
        "⛰ Shaxsiy choʻqqilar: {peaks} ({peak_owners} kishida)\n"
        "🏔 Katalogda: {catalog}, shundan foydalanuvchilardan {community} · ⏳ tekshiruvda: {pending}\n"
        "🔔 Dam olish prognoziga obunalar: {subs} ({subscribers} kishida)\n"
        "🧗 Sutkada yoʻlda boʻlganlar: {on_route_1d}\n"
        "⏱ 7 kunda chiqishlar: {trips_7d} · hozir yoʻlda: {trips_active} · ishonchli kontaktlar: {contacts}"
    ),
})


# ── nazorat muddati va ishonchli kontaktlar ──
STRINGS.update({
    "m_live_hint": (
        "📡 Translyatsiyani yoqish mumkin: 📎 → Joylashuv → <b>«Joylashuvni translyatsiya qilish»</b>. "
        "Shunda nuqta oʻzi yangilanadi — SOS va nazorat muddati uchun."
    ),
    "trip_title": "⏱ <b>Nazorat muddati</b> · {name}",
    "trip_intro": (
        "Qachongacha qaytishingizni belgilang. «✅ Qaytdim» tugmasini bosmasangiz — avval sizga eslataman, "
        "30 daqiqadan soʻng esa ishonchli kontaktlarga qayerga chiqqaningizni va yoʻldagi soʻnggi nuqtani yuboraman."
    ),
    "trip_contacts": "👥 Ishonchli kontaktlar: {names}",
    "trip_no_contacts": "👥 Ishonchli kontaktlar hali yoʻq — ularsiz faqat sizga eslataman. Pastdagi tugma bilan qoʻshing.",
    "trip_sunset": "🌅 Bugun quyosh {time} da botadi",
    "trip_pick": "Necha soatdan keyin qaytasiz? 👇\n<i>Yoki qaytish vaqtini yozing, masalan 18:30</i>",
    "trip_active_title": "⏱ <b>Siz yoʻldasiz</b> · {name}",
    "trip_started": "🚶 Chiqish {time} da",
    "trip_deadline": "🏁 <b>{time}</b> gacha qayting · {left} qoldi",
    "trip_overdue": "⏰ <b>{time}</b> muddati {late} oldin oʻtdi",
    "trip_no_point": "📍 Yoʻldan nuqta hali yoʻq — «🧗 Men yoʻldaman» boʻlimida joylashuvni yuboring.",
    "trip_point": "📍 Soʻnggi nuqta: {time} ({ago})",
    "trip_point_ele": " · ≈ {ele} m",
    "trip_alerted_note": "🚨 Kontaktlarga xavotir xabari yuborilgan — xavfsiz joyga yetishingiz bilan belgilang.",
    "trip_live_hint": (
        "<i>Maslahat: «🧗 Men yoʻldaman» boʻlimida joylashuv translyatsiyasini yoqing — nuqta oʻzi yangilanadi.</i>"
    ),
    "trip_reminder": (
        "⏰ <b>Nazorat muddati oʻtdi</b>\n\n"
        "«{name}» yoʻnalishidan {time} gacha qaytish rejalashtirilgan edi. Hammasi joyidami?\n\n"
        "30 daqiqa ichida belgilamasangiz, ishonchli kontaktlarga xavotir xabari boradi."
    ),
    "trip_alarm_title": "🚨 <b>Qaytgani haqida belgi yoʻq: {who}</b>",
    "trip_alarm_body": (
        "⛰ Yoʻnalish: «{name}» ({ele} m)\n"
        "🚶 Chiqish: {date}, {start}\n"
        "🏁 Nazorat muddati: <b>{deadline}</b> — oʻtdi, «Qaytdim» belgisi yoʻq\n"
        "👤 Profil: {who}"
    ),
    "trip_alarm_todo": (
        "<b>Nima qilish kerak</b>\n"
        "1. Bogʻlanishga urinib koʻring: {who} ga qoʻngʻiroq qiling yoki yozing.\n"
        "2. Boʻlmasa — <b>112</b> ga qoʻngʻiroq qilib, yoʻnalish, chiqish vaqti va soʻnggi nuqtani ayting.\n"
        "Qaytgani belgilanishi bilan xabar beraman."
    ),
    "trip_owner_alerted": (
        "🚨 <b>Nazorat muddati 30 daqiqa oldin oʻtdi</b>\n\n"
        "Ishonchli kontaktlarga xavotir xabari yuborildi: {names}.\n"
        "Xavfsiz joyga yetishingiz bilan «✅ Qaytdim» tugmasini bosing — ularga bekor qilish xabari boradi."
    ),
    "trip_back_notice": "✅ <b>Xavotir bekor:</b> {who} — «{name}» yoʻnalishidan qaytgani belgilandi, hammasi joyida.",
    "trip_extended_notice": "🔄 {who} aloqada va nazorat muddatini {time} gacha uzaytirmoqda.",
    "contacts_title": "👥 <b>Ishonchli kontaktlar</b>",
    "contacts_intro": (
        "Agar nazorat muddatigacha yoʻldan qaytmasangiz, ularga qayerga chiqqaningizni va soʻnggi nuqtangizni "
        "yuboraman. Odamni pastdagi tugma bilan taklif qiling: u Telegram’da havolani ochib, tasdiqlaydi. "
        "5 tagacha kontakt."
    ),
    "contacts_list": "Hozir: {names}\n<i>Kontaktni oʻchirish uchun ismini bosing.</i>",
    "contacts_empty": "Hozircha hech kim yoʻq.",
    "invite_text": (
        "👥 <b>{who}</b> sayohatlarda ishonchli kontakt boʻlishingizni soʻrayapti.\n\n"
        "Agar {who} nazorat muddatigacha yoʻldan qaytmasa, sizga qayerga chiqilganini va yoʻldagi soʻnggi "
        "nuqtani yuboraman. Boshqa hech narsa: odatdagi vaqtda joylashuv ham, xabarnomalar ham yoʻq."
    ),
    "invite_share": (
        "Sayohatlarda ishonchli kontaktim boʻl: agar yoʻldan vaqtida qaytmasam, AiroPost boti "
        "meni qayerdan qidirish kerakligini senga xabar qiladi."
    ),
    "invite_done": "✅ Tayyor! Siz {who} uchun ishonchli kontaktsiz. Biror narsa notoʻgʻri ketsa, yozaman.",
    "invite_own": "🔗 Bu sizning havolangiz — uni doʻstingiz yoki yaqiningizga yuboring.",
    "contact_added_notice": "👥 {who} endi sizning ishonchli kontaktingiz.",
    "btn_trip": "⏱ Nazorat muddati",
    "btn_trip_active": "⏱ Siz yoʻldasiz: {name}",
    "btn_trip_contacts": "👥 Ishonchli kontaktlar ({n})",
    "btn_trip_contacts_short": "👥 Kontaktlar",
    "btn_trip_done": "✅ Qaytdim",
    "btn_trip_extend": "🔄 +{h} soat",
    "btn_trip_cancel": "❌ Chiqishni bekor qilish",
    "btn_invite": "➕ Kontakt taklif qilish",
    "btn_invite_yes": "✅ Roziman",
    "btn_invite_no": "Rad etish",
    "t_trip_started": "⏱ Chiqish belgilandi — {time} gacha qayting",
    "t_trip_done": "✅ Xush kelibsiz!",
    "t_trip_extended": "🔄 Muddat {time} gacha uzaytirildi",
    "t_trip_cancelled": "Chiqish bekor qilindi",
    "t_contact_removed": "Kontakt oʻchirildi",
    "t_contacts_limit": "Bu odamda allaqachon {n} ta ishonchli kontakt bor — ortiq mumkin emas.",
    "t_invite_stale": "Taklif eskirgan — yangi havola soʻrang.",
})

# ── снег и лавинная опасность ──
STRINGS.update({
    "av_snow": "❄️ Soʻnggi 3 kunda choʻqqiga yangi qor: ≈ {recent} sm",
    "av_snow_coming": ", bir sutkada yana ≈ {coming} sm kutilmoqda",
    "av_level": "{icon} Ob-havo boʻyicha qor koʻchkisi xavfi: <b>{level}</b> — {reasons}",
    "av_levels": ["yuqori", "juda yuqori", "oʻta yuqori"],
    "av_some": "yangi qor",
    "av_fresh": "koʻp yangi qor",
    "av_lot": "kuchli qor yogʻishi",
    "av_wind": "qor yogʻayotganda shamol — qor uyumlari",
    "av_warm": "choʻqqidan yuqorigacha isish",
    "av_rain": "yangi qor ustiga yomgʻir",
    "av_note": "<i>Bu ob-havo boʻyicha baho, rasmiy qor koʻchkisi prognozi emas. Qor yoqqandan keyin 30° dan tik yonbagʻirlar xavfli.</i>",
    "gn_avalanche": "🏔 Qor koʻchkisi xavfi: qirlar va qiya yonbagʻirlardan yuring, kuluarlarni aylanib oʻting; har kimda qor koʻchkisi jihozlari boʻlsin.",
})

# ── перевалы и горнолыжка ──
STRINGS.update({
    'btn_passes': '🛣 Dovonlar',
    'btn_passes_back': '⬅️ Dovonlarga',
    'btn_ski': '⛷ Chang‘i kurortlari',
    'btn_ski_back': '⬅️ Kurortlarga',
    'btn_ski_sub': '🔔 Yangi qor haqida xabar berish',
    'btn_ski_unsub': '🔕 Yangi qor haqida xabar bermaslik',
    'road_title': '🛣 <b>Dovonlar va yoʻllar</b>',
    'road_intro': '<i>Ob-havo dovon balandligida — vodiyda emas, yoʻl oʻtgan joyda.</i>',
    'road_na': 'prognoz mavjud emas',
    'road_note': '<i>Dovonlar yopilishini YHXB va FVV eʼlon qiladi — safardan oldin rasmiy xabarlarni tekshiring.</i>',
    'road_clear': 'quruq, yogʻinsiz',
    'road_by': '{time} ga {what}',
    'road_now': '<b>Hozir</b> · {time}',
    'road_next': '<b>Yaqin sutka</b>',
    'road_days': '<b>Kunlar boʻyicha</b>',
    'road_snow': 'qor yogʻishi',
    'road_ice': 'yoʻlda muz',
    'road_rain': 'yomgʻir',
    'road_fog': 'tuman',
    'road_wind': 'kuchli shamol',
    'ski_title': '⛷ <b>Chang‘i kurortlari</b>',
    'ski_intro': '<i>Trassalar tepasidagi qor va ob-havo — yuqori stansiya balandligidagi model boʻyicha.</i>',
    'ski_snow': '❄️ Tepada yangi qor: sutkada {day} sm, 3 kunda {three} sm',
    'ski_coming': ', yana {cm} sm kutilmoqda',
    'ski_temp': '🌡 Tepada {top}, pastda {base} · 💨 {wind} m/s',
    'ski_powder': '🎉 Yangi qor — qoʻriq qorda uchish kuni!',
    'ski_lifts': '💨 Tepada kuchli shamol — koʻtargichlar toʻxtatilishi mumkin',
    'ski_days': '<b>Uchish kunlari</b> <i>(09–17)</i>',
    'ski_d_temp': 'tepada {lo}…{hi}',
    'ski_d_snow': '❄️ qor {cm} sm',
    'ski_d_wind': '💨 shamol {v} m/s gacha',
    'ski_d_fog': '🌫 tepada tuman',
    'ski_d_slush': 'pastda qor erimoqda',
    'ski_d_rain': '🌧 pastda yomgʻir',
    'ski_sub_on': '🔔 10 sm va undan koʻp yangi qor yogʻsa, ertalab yozaman.',
    'ski_sub_off': '<i>Obuna boʻlish mumkin: 10 sm va undan koʻp yangi qor yogʻsa, ertalab yozaman.</i>',
    'ski_note': '<i>Trassa balandliklari taxminiy; koʻtargichlar ishini kurortdan aniqlang.</i>',
    'ski_alert': '🎉 <b>{name}: {cm} sm yangi qor!</b>',
    't_ski_sub': '🔔 Kurortda 10 sm va undan koʻp yangi qor yogʻsa, ertalab yozaman',
    't_ski_unsub': '🔕 Qor haqidagi xabarlar oʻchirildi',
})
