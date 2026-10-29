from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from bot import locales
from bot.catalog import REGIONS
from bot.db import User
from bot.locales import LANGS
from bot.services import Place


class Nav(CallbackData, prefix="nav"):
    to: str             # home | hourly | daily | air | settings | location | time | toggle | lang
    page: int = 0
    fresh: bool = False


class PlaceCb(CallbackData, prefix="place"):
    idx: int


class TimeCb(CallbackData, prefix="time"):
    hour: int
    minute: int = -1    # -1 — час выбран, теперь показать минуты


class LangCb(CallbackData, prefix="lang"):
    code: str
    back: str = "settings"   # экран, который показать после выбора


def _btn(text: str, data: CallbackData) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=data.pack())


def _back(lang: str, to: str = "home", key: str = "btn_back") -> list[InlineKeyboardButton]:
    return [_btn(locales.get(lang)[key], Nav(to=to))]


def _lang_row(back: str) -> list[InlineKeyboardButton]:
    return [_btn(locales.get(code)["lang_name"], LangCb(code=code, back=back)) for code in LANGS]


class MCb(CallbackData, prefix="m"):
    a: str          # list | add | open | refresh | profile | hourly | outlook | route | offline | edit | del | del_yes
                    # | weekend | sub | sos
    id: int = 0
    p: int = 0      # страница или шаг времени


class GearCb(CallbackData, prefix="mg"):
    id: int         # вершина
    d: int = 0      # день: 0 — сегодня (или первый день с прогнозом)
    c: int = 0      # отмеченные вещи — биты по номерам из bot.gear.ITEMS


class TripCb(CallbackData, prefix="tr"):
    a: str          # open | start | done | extend | cancel | contacts | rm | accept
    id: int = 0     # вершина; для rm — контакт, для accept — кто приглашает
    h: int = 0      # часы до срока или продления; для rm — вершина, куда вернуться
    t: str = ""     # accept: ключ приглашения — без него контакт себе не добавить


class SpotCb(CallbackData, prefix="sp"):
    a: str          # passes | pass | ski | resort | skisub
    k: str = ""     # ключ перевала или курорта из bot.catalog


class RouteCb(CallbackData, prefix="rt"):
    a: str          # list | open | go | del
    id: int = 0     # трек
    s: str = ""     # вариант старта из bot.gpx.start_options


class PlCb(CallbackData, prefix="pl"):
    a: str          # list | go | del | save | add | trip | tdest | tlen | tset | tcancel
    id: int = 0     # место
    d: int = 0      # поездка: сдвиг первого дня от сегодня; для tset — сдвиг·100 + число дней


class PeakPickCb(CallbackData, prefix="mp"):
    idx: int


class AdminCb(CallbackData, prefix="adm"):
    a: str          # ok | no
    id: int         # заявка в каталоге


def welcome(lang: str) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_pick_place"], Nav(to="location"))],
        [_btn(loc["btn_mountains"], MCb(a="list"))],
        _lang_row("home"),
    ])


def home(lang: str) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_refresh"], Nav(to="home", fresh=True)), _btn(loc["btn_places"], PlCb(a="list"))],
        [_btn(loc["btn_hourly"], Nav(to="hourly")), _btn(loc["btn_daily"], Nav(to="daily"))],
        [_btn(loc["btn_air"], Nav(to="air")), _btn(loc["btn_mountains"], MCb(a="list"))],
        [_btn(loc["btn_passes"], SpotCb(a="passes")), _btn(loc["btn_settings"], Nav(to="settings"))],
    ])


def home_only(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[_back(lang)])


def hourly(lang: str, page: int, pages: int) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    row = []
    if page > 0:
        row.append(_btn(loc["btn_earlier"], Nav(to="hourly", page=page - 1)))
    if page < pages - 1:
        row.append(_btn(loc["btn_later"], Nav(to="hourly", page=page + 1)))
    rows = [row] if row else []
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _back(lang)])


def daily(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(locales.get(lang)["btn_hourly"], Nav(to="hourly"))],
        _back(lang),
    ])


def air(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(locales.get(lang)["btn_refresh"], Nav(to="air", fresh=True))],
        _back(lang),
    ])


def settings(user: User) -> InlineKeyboardMarkup:
    loc = locales.get(user.lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_change_place"] if user.has_location else loc["btn_pick_place"], Nav(to="location"))],
        [_btn(loc["btn_places"], PlCb(a="list"))],
        [_btn(loc("btn_time", time=user.notify_time), Nav(to="time"))],
        [_btn(loc["btn_notify_off"] if user.notify_enabled else loc["btn_notify_on"], Nav(to="toggle"))],
        [_btn(loc["btn_lang"], Nav(to="lang"))],
        _back(user.lang),
    ])


def language(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        *([_btn(locales.get(code)["lang_name"] + (" ✓" if code == lang else ""), LangCb(code=code))]
          for code in LANGS),
        _back(lang, "settings"),
    ])


def _place_back(user: User) -> str:
    return "settings" if user.has_location else "home"


def location_prompt(user: User) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[_back(user.lang, _place_back(user))])


def location_reply(lang: str, one_time: bool = True) -> ReplyKeyboardMarkup:
    loc = locales.get(lang)
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=loc["btn_send_location"], request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=one_time,
        input_field_placeholder=loc["placeholder"],
    )


def search_results(places: list[Place], user: User) -> InlineKeyboardMarkup:
    rows = [[_btn(f"📍 {p.full}", PlaceCb(idx=i))] for i, p in enumerate(places)]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _back(user.lang, _place_back(user), "btn_cancel")])


def not_found(user: User) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(locales.get(user.lang)["btn_search_again"], Nav(to="location"))],
        _back(user.lang, _place_back(user)),
    ])


def time_hours(user: User) -> InlineKeyboardMarkup:
    current = int(user.notify_time[:2])
    rows = [
        [
            _btn(f"• {h:02d} •" if h == current else f"{h:02d}", TimeCb(hour=h))
            for h in range(start, start + 6)
        ]
        for start in range(0, 24, 6)
    ]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _back(user.lang, "settings")])


def time_minutes(lang: str, hour: int) -> InlineKeyboardMarkup:
    rows = [
        [_btn(f"{hour:02d}:{m:02d}", TimeCb(hour=hour, minute=m)) for m in range(start, start + 20, 5)]
        for start in range(0, 60, 20)
    ]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _back(lang, "time")])


def error(lang: str, screen: str) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_retry"], Nav(to=screen, fresh=True))],
        [_btn(loc["btn_settings"], Nav(to="settings"))],
    ])


# ── горы ────────────────────────────────────────────────────────────────────

def _to_peak(lang: str, peak_id: int) -> list[InlineKeyboardButton]:
    return [_btn(locales.get(lang)["btn_m_to_peak"], MCb(a="open", id=peak_id))]


def _to_list(lang: str) -> list[InlineKeyboardButton]:
    return [_btn(locales.get(lang)["btn_m_back"], MCb(a="list"))]


def mountains(lang: str, peaks: list, can_add: bool, catalog_count: int = 0, trip=None) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    rows = [[_btn(loc("btn_trip_active", name=trip.peak_name), TripCb(a="open", id=trip.peak_id))]] if trip else []
    if catalog_count:
        rows.append([_btn(loc("m_catalog_btn", n=catalog_count), MCb(a="cat"))])
    if catalog_count or peaks:
        rows.append([_btn(loc["btn_m_weekend"], MCb(a="weekend"))])
    rows += [[_btn(f"⛰ {p.name} · {p.ele} {loc['m']}", MCb(a="open", id=p.id))] for p in peaks]
    if can_add:
        rows.append([_btn(loc["btn_m_add"], MCb(a="add"))])
    rows.append([_btn(loc["btn_ski"], SpotCb(a="ski")), _btn(loc["btn_passes"], SpotCb(a="passes"))])
    rows.append([_btn(loc["btn_routes"], RouteCb(a="list"))])
    rows.append([_btn(loc["btn_sos"], MCb(a="sos"))])
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _back(lang)])


def mountain_add(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[_to_list(lang)])


def peak_results(lang: str, labels: list[str]) -> InlineKeyboardMarkup:
    rows = [[_btn(f"⛰ {label}", PeakPickCb(idx=i))] for i, label in enumerate(labels)]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _to_list(lang)])


def peak_not_found(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(locales.get(lang)["btn_search_again"], MCb(a="add"))],
        _to_list(lang),
    ])


def catalog(lang: str, regions: list[tuple[str, int]]) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    rows = [
        [_btn(f"🗺 {loc['region_' + region]} ({count})", MCb(a="reg", id=REGIONS.index(region)))]
        for region, count in regions
    ]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _to_list(lang)])


def catalog_region(lang: str, region: str, peaks: list, page: int, pages: int) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    region_id = REGIONS.index(region)
    rows = [[_btn(f"⛰ {p.name} · {p.ele} {loc['m']}", MCb(a="open", id=p.id))] for p in peaks]
    nav = []
    if page > 0:
        nav.append(_btn(loc["btn_earlier"], MCb(a="reg", id=region_id, p=page - 1)))
    if page < pages - 1:
        nav.append(_btn(loc["btn_later"], MCb(a="reg", id=region_id, p=page + 1)))
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=[*rows, [_btn(loc["btn_m_catalog_back"], MCb(a="cat"))]])


def peak(
    lang: str, p, can_publish: bool = False, subscribed: bool = False, share_url: str | None = None,
) -> InlineKeyboardMarkup:
    """Вершина из каталога — только просмотр; своя — ещё правка, удаление и публикация."""
    loc = locales.get(lang)
    bottom = [_btn(loc["btn_m_offline"], MCb(a="offline", id=p.id))]
    if share_url:
        bottom.append(InlineKeyboardButton(text=loc["btn_m_share"], url=share_url))
    rows = [
        [_btn(loc["btn_refresh"], MCb(a="refresh", id=p.id))],
        [_btn(loc["btn_m_profile"], MCb(a="profile", id=p.id)),
         _btn(loc["btn_m_hourly"], MCb(a="hourly", id=p.id))],
        [_btn(loc["btn_m_outlook"], MCb(a="outlook", id=p.id)), _btn(loc["btn_m_gear"], GearCb(id=p.id))],
        [_btn(loc["btn_m_route"], MCb(a="route", id=p.id)), _btn(loc["btn_trip"], TripCb(a="open", id=p.id))],
        bottom,
        [_btn(loc["btn_m_unsub" if subscribed else "btn_m_sub"], MCb(a="sub", id=p.id))],
    ]
    if p.public:
        region = p.region if p.region in REGIONS else "community"
        rows.append([_btn(loc["btn_m_catalog_back"], MCb(a="reg", id=REGIONS.index(region)))])
        return InlineKeyboardMarkup(inline_keyboard=rows)
    if can_publish and p.status in (None, "rejected"):
        rows.append([_btn(loc["btn_m_publish"], MCb(a="pub", id=p.id))])
    rows.append([_btn(loc["btn_m_ele"], MCb(a="edit", id=p.id)), _btn(loc["btn_m_delete"], MCb(a="del", id=p.id))])
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _to_list(lang)])


def publish_confirm(lang: str, peak_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(locales.get(lang)["btn_m_publish_yes"], MCb(a="pub_yes", id=peak_id))],
        _to_peak(lang, peak_id),
    ])


def admin_request(lang: str, request_id: int) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[[
        _btn(loc["btn_a_approve"], AdminCb(a="ok", id=request_id)),
        _btn(loc["btn_a_reject"], AdminCb(a="no", id=request_id)),
    ]])


def peak_profile(lang: str, peak_id: int, step: int, max_step: int) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    row = []
    if step > 0:
        row.append(_btn(loc["btn_m_minus"], MCb(a="profile", id=peak_id, p=step - 1)))
        row.append(_btn(loc["btn_m_now"], MCb(a="profile", id=peak_id)))
    if step < max_step:
        row.append(_btn(loc["btn_m_plus"], MCb(a="profile", id=peak_id, p=step + 1)))
    return InlineKeyboardMarkup(inline_keyboard=[row, _to_peak(lang, peak_id)])


def peak_hourly(lang: str, peak_id: int, page: int, pages: int) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    row = []
    if page > 0:
        row.append(_btn(loc["btn_earlier"], MCb(a="hourly", id=peak_id, p=page - 1)))
    if page < pages - 1:
        row.append(_btn(loc["btn_later"], MCb(a="hourly", id=peak_id, p=page + 1)))
    rows = [row] if row else []
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _to_peak(lang, peak_id)])


def peak_back(lang: str, peak_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[_to_peak(lang, peak_id)])


def peak_route(lang: str, peak_id: int) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_m_profile"], MCb(a="profile", id=peak_id)), _btn(loc["btn_sos"], MCb(a="sos", id=peak_id))],
        [_btn(loc["btn_trip"], TripCb(a="open", id=peak_id))],
        _to_peak(lang, peak_id),
    ])


# ── контрольный срок ────────────────────────────────────────────────────────

def trip_setup(lang: str, peak_id: int, options: list[tuple[int, str]], contacts: int) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    buttons = [_btn(label, TripCb(a="start", id=peak_id, h=h)) for h, label in options]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    rows.append([_btn(loc("btn_trip_contacts", n=contacts), TripCb(a="contacts", id=peak_id))])
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _to_peak(lang, peak_id)])


def _trip_return_row(lang: str, trip_peak: int) -> list[list[InlineKeyboardButton]]:
    loc = locales.get(lang)
    return [
        [_btn(loc["btn_trip_done"], TripCb(a="done", id=trip_peak))],
        [_btn(loc("btn_trip_extend", h=h), TripCb(a="extend", id=trip_peak, h=h)) for h in (1, 2)],
    ]


def trip_active(lang: str, peak_id: int) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        *_trip_return_row(lang, peak_id),
        [_btn(loc["btn_m_route"], MCb(a="route", id=peak_id)), _btn(loc["btn_sos"], MCb(a="sos", id=peak_id))],
        [_btn(loc("btn_trip_contacts_short"), TripCb(a="contacts", id=peak_id)),
         _btn(loc["btn_trip_cancel"], TripCb(a="cancel", id=peak_id))],
        _to_peak(lang, peak_id),
    ])


def trip_reminder(lang: str, peak_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=_trip_return_row(lang, peak_id))


def contacts(lang: str, people: list[tuple[int, str]], peak_id: int, invite_url: str | None) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    rows = [[_btn(f"❌ {name}", TripCb(a="rm", id=cid, h=peak_id))] for cid, name in people]
    if invite_url:
        rows.append([InlineKeyboardButton(text=loc["btn_invite"], url=invite_url)])
    back = [_btn(loc["btn_back"], TripCb(a="open", id=peak_id))] if peak_id else _to_list(lang)
    return InlineKeyboardMarkup(inline_keyboard=[*rows, back])


def invite(lang: str, owner_id: int, token: str) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_invite_yes"], TripCb(a="accept", id=owner_id, t=token))],
        [_btn(loc["btn_invite_no"], Nav(to="home"))],
    ])


def gear(lang: str, peak_id: int, days: list[str], day: int, items: list, mask: int) -> InlineKeyboardMarkup:
    """Дни сверху, под ними вещи по две в ряд: нажатие отмечает вещь собранной."""
    day_row = [
        _btn(f"• {label} •" if i == day else label, GearCb(id=peak_id, d=i, c=mask))
        for i, label in enumerate(days)
    ]
    loc = locales.get(lang)
    buttons = [
        _btn(f"{'✅' if mask & item.bit else '⬜'} {loc['g_' + item.key]}", GearCb(id=peak_id, d=day, c=mask ^ item.bit))
        for item in items
    ]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=[day_row, *rows, _to_peak(lang, peak_id)])


def _peak_buttons(entries: list, limit: int = 8) -> list[list[InlineKeyboardButton]]:
    return [[_btn(f"⛰ {e.peak.name}", MCb(a="open", id=e.peak.id))] for e in entries[:limit]]


def weekend(lang: str, entries: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[*_peak_buttons(entries), _to_list(lang)])


def digest(lang: str, entries: list) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        *_peak_buttons(entries),
        [_btn(loc["btn_m_weekend"], MCb(a="weekend"))],
        [_btn(loc["btn_mountains"], MCb(a="list"))],
    ])


def changes(lang: str, peaks: list) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    rows = [[_btn(f"⛰ {p.name}", MCb(a="open", id=p.id))] for p in peaks[:8]]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, [_btn(loc["btn_mountains"], MCb(a="list"))]])


def sos(lang: str, peak_id: int = 0, share_url: str | None = None) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    rows = [[InlineKeyboardButton(text=loc["btn_sos_share"], url=share_url)]] if share_url else []
    back = _to_peak(lang, peak_id) if peak_id else _to_list(lang)
    return InlineKeyboardMarkup(inline_keyboard=[*rows, back])


def peak_delete(lang: str, peak_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(locales.get(lang)["btn_m_yes_delete"], MCb(a="del_yes", id=peak_id))],
        _to_peak(lang, peak_id),
    ])


def peak_error(lang: str, peak_id: int) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_retry"], MCb(a="refresh", id=peak_id))],
        _to_list(lang),
    ])


# ── перевалы и горнолыжка ───────────────────────────────────────────────────

def passes(lang: str, items: list) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    rows = [[_btn(f"🛣 {p.name}", SpotCb(a="pass", k=p.key))] for p in items]
    return InlineKeyboardMarkup(inline_keyboard=[
        *rows, [_btn(loc["btn_refresh"], SpotCb(a="passes"))], [_btn(loc["btn_mountains"], MCb(a="list"))], _back(lang),
    ])


def pass_detail(lang: str, key: str) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_refresh"], SpotCb(a="pass", k=key))],
        [_btn(loc["btn_passes_back"], SpotCb(a="passes"))],
    ])


def ski(lang: str, items: list) -> InlineKeyboardMarkup:
    rows = [[_btn(f"⛷ {r.name}", SpotCb(a="resort", k=r.key))] for r in items]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _to_list(lang)])


def resort(lang: str, key: str, subscribed: bool) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_refresh"], SpotCb(a="resort", k=key))],
        [_btn(loc["btn_ski_unsub" if subscribed else "btn_ski_sub"], SpotCb(a="skisub", k=key))],
        [_btn(loc["btn_ski_back"], SpotCb(a="ski"))],
    ])


# ── GPX-треки ───────────────────────────────────────────────────────────────

def routes(lang: str, items: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    rows = [[_btn(f"🗺 {name}", RouteCb(a="open", id=rid))] for rid, name in items]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _to_list(lang)])


def route_start(lang: str, route_id: int, options: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    buttons = [_btn(label, RouteCb(a="go", id=route_id, s=code)) for code, label in options]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=[
        *rows,
        [_btn(loc["btn_route_del"], RouteCb(a="del", id=route_id))],
        [_btn(loc["btn_routes_back"], RouteCb(a="list"))],
    ])


def route_plan(lang: str, route_id: int) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(loc["btn_route_other_start"], RouteCb(a="open", id=route_id))],
        [_btn(loc["btn_routes_back"], RouteCb(a="list"))],
    ])


# ── избранные места и поездки ───────────────────────────────────────────────

def places(lang: str, items: list, can_save: bool, can_add: bool, trip: bool) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    rows = [[_btn(f"📍 {p.name}", PlCb(a="go", id=p.id)), _btn("🗑", PlCb(a="del", id=p.id))] for p in items]
    if can_save:
        rows.append([_btn(loc["btn_pl_save"], PlCb(a="save"))])
    if can_add:
        rows.append([_btn(loc["btn_pl_add"], PlCb(a="add"))])
    trip_row = [_btn(loc["btn_pl_trip_cancel"], PlCb(a="tcancel"))] if trip else [_btn(loc["btn_pl_trip"], PlCb(a="trip"))]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, trip_row, _back(lang, "settings")])


def _to_places(lang: str) -> list[InlineKeyboardButton]:
    return [_btn(locales.get(lang)["btn_pl_back"], PlCb(a="list"))]


def places_back(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[_to_places(lang)])


def trip_dest(lang: str, items: list) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    rows = [[_btn(f"✈️ {p.name}", PlCb(a="tdest", id=p.id))] for p in items]
    rows.append([_btn(loc["btn_pl_add"], PlCb(a="add"))])
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _to_places(lang)])


def trip_from(lang: str, place_id: int, labels: list[str]) -> InlineKeyboardMarkup:
    buttons = [_btn(label, PlCb(a="tlen", id=place_id, d=i)) for i, label in enumerate(labels)]
    rows = [buttons[i:i + 4] for i in range(0, len(buttons), 4)]
    return InlineKeyboardMarkup(inline_keyboard=[*rows, _to_places(lang)])


def trip_len(lang: str, place_id: int, offset: int) -> InlineKeyboardMarkup:
    loc = locales.get(lang)
    buttons = [_btn(loc("pl_days", n=n), PlCb(a="tset", id=place_id, d=offset * 100 + n))
               for n in (1, 2, 3, 4, 5, 7, 10, 14)]
    return InlineKeyboardMarkup(inline_keyboard=[buttons[:4], buttons[4:], _to_places(lang)])
