"""Модерация: админ одобряет или отклоняет вершины, которые пользователи предлагают в общий каталог."""
import logging
import sqlite3
from datetime import datetime
from html import escape
from pathlib import Path

from aiogram import Bot, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from aiogram.types import CallbackQuery, FSInputFile, LinkPreviewOptions, Message, User as TgUser

from bot import keyboards as kb
from bot import locales, ui
from bot import mountain_texts as mt
from bot.db import MAX_PEAKS, Database
from bot.keyboards import AdminCb

log = logging.getLogger(__name__)
router = Router(name="admin")

NO_PREVIEW = LinkPreviewOptions(is_disabled=True)


def author_html(user_id: int, name: str | None = None, username: str | None = None) -> str:
    text = f'<a href="tg://user?id={user_id}">{escape(name or str(user_id))}</a>'
    if username:
        text += f" @{escape(username)}"
    return f"{text} · <code>{user_id}</code>"


async def notify_admins(bot: Bot, db: Database, admins: frozenset[int], request_id: int, author: str) -> int:
    """Разослать заявку админам. Возвращает, скольким удалось доставить."""
    row = await db.request(request_id)
    delivered = 0
    for admin_id in admins:
        lang = (await db.get_user(admin_id)).lang
        text = mt.admin_request(lang, request_id, row["name_ru"], row["ele"], row["lat"], row["lon"], author)
        try:
            # Отдельное сообщение-задача: остаётся у админа, пока он не примет решение
            await bot.send_message(
                admin_id, text, reply_markup=kb.admin_request(lang, request_id), link_preview_options=NO_PREVIEW,
            )
            delivered += 1
        except TelegramAPIError as e:
            log.warning("Заявка #%s не доставлена админу %s: %s", request_id, admin_id, e)
    return delivered


@router.callback_query(AdminCb.filter())
async def on_review(
    callback: CallbackQuery,
    callback_data: AdminCb,
    bot: Bot,
    db: Database,
    admins: frozenset[int],
    fsm_storage: BaseStorage,
) -> None:
    admin = callback.from_user
    loc = locales.get((await db.get_user(admin.id)).lang)
    if admin.id not in admins:
        await callback.answer(loc["t_a_forbidden"], show_alert=True)
        return

    approved = callback_data.a == "ok"
    row = await db.review(callback_data.id, approved, admin.id)
    if row is None:
        # Уже решил другой админ (или заявку отменили) — просто убираем кнопки
        if callback.message:
            try:
                await callback.message.edit_reply_markup(reply_markup=None)
            except TelegramAPIError:
                pass
        await callback.answer(loc["t_a_done"], show_alert=True)
        return

    verdict = loc("a_approved" if approved else "a_rejected", admin=escape(admin.full_name))
    if callback.message:
        try:
            await callback.message.edit_text(
                f"{callback.message.html_text}\n\n{verdict}", reply_markup=None, link_preview_options=NO_PREVIEW,
            )
        except TelegramAPIError:
            pass
    await callback.answer(loc["t_a_approved"] if approved else loc["t_a_rejected"])
    await _notify_author(bot, db, fsm_storage, row, approved)


async def _notify_author(bot: Bot, db: Database, storage: BaseStorage, row, approved: bool) -> None:
    """Сообщить автору о решении. Как и ежедневная сводка, это новое сообщение внизу чата,
    а прежнее меню удаляется — в чате по-прежнему одно сообщение бота."""
    author_id = row["author_id"]
    if not author_id:
        return
    user = await db.get_user(author_id)
    loc = locales.get(user.lang)
    notice = loc("m_published_notice" if approved else "m_rejected_notice", name=escape(row["name_ru"]))
    peaks = await db.peaks(author_id)
    catalog = await db.catalog(user.lang)
    text = f"{notice}\n\n{mt.mountains(user.lang, peaks)}"
    markup = kb.mountains(user.lang, peaks, len(peaks) < MAX_PEAKS, len(catalog))
    state = FSMContext(storage, StorageKey(bot_id=bot.id, chat_id=author_id, user_id=author_id))
    try:
        await ui.leave_location_mode(bot, state, author_id)
        await ui.send_fresh(bot, db, author_id, text, markup)
    except TelegramAPIError as e:
        log.info("Автор %s не получил решение по заявке #%s: %s", author_id, row["id"], e)


@router.message(Command("pending"))
async def cmd_pending(message: Message, bot: Bot, db: Database, admins: frozenset[int]) -> None:
    """Для админа: заново прислать все заявки, ждущие проверки (например, если сообщения потерялись)."""
    await ui.delete_incoming(message)
    if message.from_user.id not in admins:
        return
    pending = await db.pending_requests()
    lang = (await db.get_user(message.from_user.id)).lang
    if not pending:
        await ui.show(bot, db, message.chat.id, locales.get(lang)["a_no_pending"], kb.mountain_add(lang))
        return
    for row in pending:
        await notify_admins(bot, db, frozenset({message.from_user.id}), row["id"], author_html(row["author_id"]))


def tg_author(user: TgUser) -> str:
    return author_html(user.id, user.full_name, user.username)


@router.message(Command("stats"))
async def cmd_stats(message: Message, bot: Bot, db: Database, admins: frozenset[int]) -> None:
    """Для админа: сколько пользователей, кто активен, чем пользуются."""
    await ui.delete_incoming(message)
    if message.from_user.id not in admins:
        return
    lang = (await db.get_user(message.from_user.id)).lang
    await ui.send_fresh(bot, db, message.chat.id, locales.get(lang)("a_stats", **await db.stats()), kb.home_only(lang))


@router.message(Command("backup"))
async def cmd_backup(message: Message, bot: Bot, db: Database, admins: frozenset[int], backups: Path) -> None:
    """Для админа: свежая копия базы файлом в чат — чтобы хранить её не только на сервере."""
    await ui.delete_incoming(message)
    if message.from_user.id not in admins:
        return
    path = backups / f"manual-{datetime.now():%Y-%m-%d-%H%M%S}.db"
    try:
        await db.backup(path)
        await bot.send_document(message.chat.id, FSInputFile(path, filename=f"airopost-{path.stem[7:]}.db"))
    except (OSError, sqlite3.Error, TelegramAPIError) as e:
        log.warning("Не удалось отправить копию базы: %s", e)
    finally:
        path.unlink(missing_ok=True)
