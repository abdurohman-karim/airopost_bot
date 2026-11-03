"""Отчёты об условиях на тропе: люди отмечают, что видели (лёд, снег, вода, брод, собаки), и пишут
пару слов или присылают фото. Отчёт сразу виден всем 7 дней, админ получает копию с кнопкой «Скрыть»."""
import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InputMediaPhoto, Message

from bot import keyboards as kb
from bot import locales, ui
from bot import report_texts as rt
from bot.db import REPORTS_PER_DAY, Database, Peak
from bot.keyboards import RepCb
from bot.states import Form

log = logging.getLogger(__name__)
router = Router(name="reports")


async def reports_screen(
    db: Database, chat_id: int, lang: str, peak: Peak, header: str | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    items = await db.reports(peak.catalog_id)
    own = next((r.id for r in items if r.user_id == chat_id), None)
    photos = sum(1 for r in items if r.photo_id)
    return rt.reports_screen(lang, peak, items, header), kb.reports(lang, peak.id, photos, own)


async def _draft_screen(state: FSMContext, lang: str, peak: Peak, error: str | None = None):
    data = await state.get_data()
    mask, text, photo = data.get("tags", 0), data.get("text"), data.get("photo")
    labels = rt.tag_labels(locales.get(lang))
    markup = kb.report_draft(lang, peak.id, labels, mask, ready=bool(mask or text or photo))
    return rt.draft(lang, peak, mask, text, bool(photo), error), markup


async def _notify_admins(bot: Bot, db: Database, admins: frozenset[int], peak: Peak, report) -> None:
    for admin_id in admins:
        lang = (await db.get_user(admin_id)).lang
        text, markup = rt.admin_copy(lang, peak.name, report), kb.report_admin(lang, report.id)
        try:
            if report.photo_id:
                await bot.send_photo(admin_id, report.photo_id, caption=text[:1024], reply_markup=markup)
            else:
                await bot.send_message(admin_id, text, reply_markup=markup)
        except TelegramAPIError as e:
            log.warning("Копия отчёта #%s не доставлена админу %s: %s", report.id, admin_id, e)


@router.callback_query(RepCb.filter())
async def on_report(
    callback: CallbackQuery, callback_data: RepCb, bot: Bot, state: FSMContext, db: Database,
    admins: frozenset[int],
) -> None:
    chat_id, message_id = callback.from_user.id, callback.message.message_id if callback.message else None
    lang = (await db.get_user(chat_id)).lang
    loc = locales.get(lang)
    action = callback_data.a

    if action == "hide":
        if chat_id not in admins:
            await callback.answer(loc["t_a_forbidden"], show_alert=True)
            return
        await db.hide_report(callback_data.id)
        if callback.message:
            try:
                await callback.message.edit_reply_markup(reply_markup=None)
            except TelegramAPIError:
                pass
        await callback.answer(loc["t_rep_hidden"])
        return
    if action == "mine":
        report = await db.report(callback_data.id)
        if report:
            await db.hide_report(report.id, chat_id)
        peak = await db.catalog_peak(report.catalog_id, lang) if report else None
        if peak:
            await ui.show(bot, db, chat_id, *await reports_screen(db, chat_id, lang, peak), message_id)
        await callback.answer(loc["t_rep_deleted"])
        return

    peak = await db.resolve_peak(chat_id, callback_data.id, lang)
    if not peak or not peak.public:
        await callback.answer(loc["t_m_missing"], show_alert=True)
        return

    if action == "add":
        if await db.reports_today(chat_id) >= REPORTS_PER_DAY:
            await callback.answer(loc("t_rep_limit", n=REPORTS_PER_DAY), show_alert=True)
            return
        await ui.leave_location_mode(bot, state, chat_id)
        await state.set_state(Form.report)
        await state.update_data(peak_id=peak.id, tags=0, text=None, photo=None)
        await ui.show(bot, db, chat_id, *await _draft_screen(state, lang, peak), message_id)
    elif action == "tag":
        if await state.get_state() != Form.report.state:
            await state.set_state(Form.report)
            await state.update_data(peak_id=peak.id, tags=0, text=None, photo=None)
        mask = (await state.get_data()).get("tags", 0) ^ (1 << min(max(callback_data.t, 0), len(rt.TAGS) - 1))
        await state.update_data(tags=mask)
        await ui.show(bot, db, chat_id, *await _draft_screen(state, lang, peak), message_id)
    elif action == "send":
        data = await state.get_data()
        mask, text, photo = data.get("tags", 0), data.get("text"), data.get("photo")
        if await state.get_state() != Form.report.state or not (mask or text or photo):
            await callback.answer(loc["t_rep_empty"], show_alert=True)
            return
        report = await db.add_report(peak.catalog_id, chat_id, callback.from_user.full_name, mask, text, photo)
        await state.clear()
        await ui.show(bot, db, chat_id, *await reports_screen(db, chat_id, lang, peak, loc["t_rep_sent"]), message_id)
        await callback.answer(loc["t_rep_sent"])
        await _notify_admins(bot, db, admins, peak, report)
        return
    elif action == "photos":
        photos = [r for r in await db.reports(peak.catalog_id) if r.photo_id][:10]
        if photos:
            media = [InputMediaPhoto(media=r.photo_id, caption=f"{r.user_name} · {rt.ago(loc, r.created_at)}")
                     for r in photos]
            # Фото — отдельными сообщениями, как офлайн-прогноз; меню затем снова внизу
            await bot.send_media_group(chat_id, media)
            await ui.send_fresh(bot, db, chat_id, *await reports_screen(db, chat_id, lang, peak))
    else:
        await ui.leave_location_mode(bot, state, chat_id)
        await ui.show(bot, db, chat_id, *await reports_screen(db, chat_id, lang, peak), message_id)
    await callback.answer()


@router.message(Form.report, F.photo)
async def on_report_photo(message: Message, bot: Bot, state: FSMContext, db: Database) -> None:
    caption = (message.caption or "").strip()[:rt.MAX_TEXT] or None
    await state.update_data(photo=message.photo[-1].file_id, **({"text": caption} if caption else {}))
    await _redraw(message, bot, state, db)


@router.message(Form.report, F.text, ~F.text.startswith("/"))
async def on_report_text(message: Message, bot: Bot, state: FSMContext, db: Database) -> None:
    await state.update_data(text=message.text.strip()[:rt.MAX_TEXT])
    await _redraw(message, bot, state, db)


async def _redraw(message: Message, bot: Bot, state: FSMContext, db: Database) -> None:
    chat_id = message.chat.id
    await ui.delete_incoming(message)
    lang = (await db.get_user(chat_id)).lang
    peak = await db.resolve_peak(chat_id, (await state.get_data()).get("peak_id") or 0, lang)
    if peak:
        await ui.show(bot, db, chat_id, *await _draft_screen(state, lang, peak))
