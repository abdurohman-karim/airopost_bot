"""Тексты отчётов об условиях на тропе."""
from __future__ import annotations

from html import escape

from bot import locales, timeutil
from bot.db import Peak, Report
from bot.locales import Locale

# Номер отметки — бит в reports.tags. Порядок не менять, новые — только в конец.
TAGS = ("dry", "mud", "snow", "ice", "water", "nowater", "ford", "dogs")
TAG_ICONS = {"dry": "✅", "mud": "🟤", "snow": "❄️", "ice": "🧊", "water": "💧", "nowater": "🚱", "ford": "🌊", "dogs": "🐕"}
SHOWN = 6
MAX_TEXT = 500


def tag_labels(loc: Locale) -> list[tuple[int, str]]:
    return [(i, f"{TAG_ICONS[t]} {loc['tag_' + t]}") for i, t in enumerate(TAGS)]


def tags_text(loc: Locale, mask: int) -> str:
    return ", ".join(f"{TAG_ICONS[t]} {loc['tag_' + t]}" for i, t in enumerate(TAGS) if mask & (1 << i))


def ago(loc: Locale, created_at: str) -> str:
    hours = int((timeutil.utc_now() - timeutil.from_db(created_at)).total_seconds() // 3600)
    if hours < 1:
        return loc["rep_now"]
    if hours < 24:
        return loc("rep_hours", n=hours)
    return loc("rep_days", n=hours // 24)


def _line(loc: Locale, r: Report) -> str:
    parts = [p for p in (tags_text(loc, r.tags), escape(r.text) if r.text else None) if p]
    photo = " 📷" if r.photo_id else ""
    return f"🗣 <b>{escape(r.user_name)}</b> · {ago(loc, r.created_at)}{photo}\n" + ("\n".join(parts) or "—")


def latest(lang: str, reports: list[Report]) -> str | None:
    """Строка на странице вершины: самый свежий отчёт."""
    if not reports:
        return None
    loc = locales.get(lang)
    r = reports[0]
    what = tags_text(loc, r.tags) or (escape(r.text[:60]) + ("…" if len(r.text) > 60 else "") if r.text else "📷")
    return loc("rep_latest", ago=ago(loc, r.created_at), what=what)


def reports_screen(lang: str, peak: Peak, reports: list[Report], header: str | None = None) -> str:
    loc = locales.get(lang)
    lines = [header, ""] if header else []
    lines += [loc("rep_title", name=escape(peak.name)), loc["rep_intro"], ""]
    if not reports:
        lines.append(loc["rep_empty"])
    for r in reports[:SHOWN]:
        lines += [_line(loc, r), ""]
    if len(reports) > SHOWN:
        lines.append(loc("rep_more", n=len(reports) - SHOWN))
    return "\n".join(lines).rstrip()


def draft(lang: str, peak: Peak, mask: int, text: str | None, photo: bool, error: str | None = None) -> str:
    loc = locales.get(lang)
    lines = [loc[error], ""] if error else []
    lines += [loc("rep_add_title", name=escape(peak.name)), "", loc["rep_add_intro"]]
    if mask or text or photo:
        lines += ["", loc["rep_draft"]]
        if mask:
            lines.append(tags_text(loc, mask))
        if text:
            lines.append(f"<i>{escape(text)}</i>")
        if photo:
            lines.append(loc["rep_photo_attached"])
    return "\n".join(lines)


def admin_copy(lang: str, peak_name: str, r: Report) -> str:
    loc = locales.get(lang)
    return loc("rep_admin", name=escape(peak_name)) + "\n\n" + _line(loc, r) + f"\n<code>{r.user_id}</code>"
