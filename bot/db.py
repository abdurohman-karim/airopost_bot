from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import aiosqlite

from bot.locales import DEFAULT as DEFAULT_LANG

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id        INTEGER PRIMARY KEY,
    lat            REAL,
    lon            REAL,
    place          TEXT,
    tz             TEXT,
    notify_time    TEXT    NOT NULL,
    notify_enabled INTEGER NOT NULL DEFAULT 1,
    last_sent      TEXT,             -- местная дата последней рассылки, YYYY-MM-DD
    menu_msg_id    INTEGER,          -- «живое» сообщение бота, которое редактируется
    lang           TEXT,             -- ru | uz | en
    created_at     TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS peaks (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    name       TEXT    NOT NULL,
    lat        REAL    NOT NULL,
    lon        REAL    NOT NULL,
    ele        INTEGER NOT NULL,
    catalog_id INTEGER,              -- заявка на публикацию в общий каталог
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS peaks_user ON peaks (user_id);

-- Общий каталог: встроенные вершины (slug) и одобренные админом вершины пользователей
CREATE TABLE IF NOT EXISTS catalog (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    slug           TEXT UNIQUE,
    name_ru        TEXT    NOT NULL,
    name_uz        TEXT    NOT NULL,
    name_en        TEXT    NOT NULL,
    region         TEXT    NOT NULL DEFAULT 'community',
    lat            REAL    NOT NULL,
    lon            REAL    NOT NULL,
    ele            INTEGER NOT NULL,
    status         TEXT    NOT NULL DEFAULT 'approved',   -- pending | approved | rejected
    author_id      INTEGER,
    source_peak_id INTEGER,
    reviewer_id    INTEGER,
    reviewed_at    TEXT,
    created_at     TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS catalog_status ON catalog (status);
"""

COLUMNS = {"lat", "lon", "place", "tz", "notify_time", "notify_enabled", "last_sent", "menu_msg_id", "lang"}

# Колонки, добавленные после первой версии: (таблица, имя, тип) — для обновления старых баз
MIGRATIONS = [("users", "lang", "TEXT"), ("peaks", "catalog_id", "INTEGER")]


@dataclass
class User:
    user_id: int
    lat: float | None
    lon: float | None
    place: str | None
    tz: str | None
    notify_time: str
    notify_enabled: bool
    last_sent: str | None
    menu_msg_id: int | None
    lang: str = DEFAULT_LANG

    @property
    def has_location(self) -> bool:
        return self.lat is not None and self.lon is not None

    @classmethod
    def from_row(cls, row: aiosqlite.Row) -> User:
        return cls(
            user_id=row["user_id"],
            lat=row["lat"],
            lon=row["lon"],
            place=row["place"],
            tz=row["tz"],
            notify_time=row["notify_time"],
            notify_enabled=bool(row["notify_enabled"]),
            last_sent=row["last_sent"],
            menu_msg_id=row["menu_msg_id"],
            lang=row["lang"] or DEFAULT_LANG,
        )


@dataclass
class Peak:
    id: int                      # > 0 — личная вершина, < 0 — вершина общего каталога (−id в каталоге)
    name: str
    lat: float
    lon: float
    ele: int
    status: str | None = None    # личная: заявка на публикацию — None | pending | approved | rejected
    region: str | None = None    # каталог: ключ региона из bot.catalog.REGIONS
    author_id: int | None = None  # каталог: кто предложил (None — встроенная вершина)

    @property
    def public(self) -> bool:
        return self.id < 0

    @property
    def catalog_id(self) -> int:
        return -self.id


MAX_PEAKS = 10
NAME_COLUMNS = {"ru": "name_ru", "uz": "name_uz", "en": "name_en"}


class Database:
    def __init__(self, path: str, default_time: str) -> None:
        self._path = path
        self._default_time = default_time
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self._path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA)
        for table, name, kind in MIGRATIONS:
            async with self._conn.execute(f"PRAGMA table_info({table})") as cur:
                existing = {row["name"] for row in await cur.fetchall()}
            if name not in existing:
                await self._conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {kind}")
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()

    @property
    def conn(self) -> aiosqlite.Connection:
        assert self._conn, "Database.connect() не вызван"
        return self._conn

    async def ensure_user(self, user_id: int, lang: str) -> None:
        """Создать пользователя при первом обращении, сразу с языком из Telegram."""
        await self.conn.execute(
            "INSERT OR IGNORE INTO users (user_id, notify_time, lang) VALUES (?, ?, ?)",
            (user_id, self._default_time, lang),
        )
        await self.conn.commit()

    async def get_user(self, user_id: int) -> User:
        """Возвращает пользователя, создавая запись при первом обращении."""
        await self.conn.execute(
            "INSERT OR IGNORE INTO users (user_id, notify_time) VALUES (?, ?)",
            (user_id, self._default_time),
        )
        await self.conn.commit()
        async with self.conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            return User.from_row(await cur.fetchone())

    async def update(self, user_id: int, **fields) -> User:
        unknown = fields.keys() - COLUMNS
        if unknown:
            raise ValueError(f"Неизвестные поля: {unknown}")
        if fields:
            assignments = ", ".join(f"{k} = ?" for k in fields)
            await self.conn.execute(
                f"UPDATE users SET {assignments} WHERE user_id = ?", (*fields.values(), user_id)
            )
            await self.conn.commit()
        return await self.get_user(user_id)

    async def subscribers(self) -> list[User]:
        async with self.conn.execute(
            "SELECT * FROM users WHERE notify_enabled = 1 AND lat IS NOT NULL AND lon IS NOT NULL"
        ) as cur:
            return [User.from_row(row) for row in await cur.fetchall()]

    # ── личные вершины: видны только их владельцу ──

    _PEAK_SELECT = (
        "SELECT p.id, p.name, p.lat, p.lon, p.ele, c.status "
        "FROM peaks p LEFT JOIN catalog c ON c.id = p.catalog_id "
    )

    async def peaks(self, user_id: int) -> list[Peak]:
        async with self.conn.execute(self._PEAK_SELECT + "WHERE p.user_id = ? ORDER BY p.id", (user_id,)) as cur:
            return [Peak(*row) for row in await cur.fetchall()]

    async def peak(self, user_id: int, peak_id: int) -> Peak | None:
        async with self.conn.execute(
            self._PEAK_SELECT + "WHERE p.user_id = ? AND p.id = ?", (user_id, peak_id)
        ) as cur:
            row = await cur.fetchone()
        return Peak(*row) if row else None

    async def resolve_peak(self, user_id: int, peak_id: int, lang: str) -> Peak | None:
        """Вершина по id из кнопки: своя (id > 0) или из общего каталога (id < 0)."""
        if peak_id < 0:
            return await self.catalog_peak(-peak_id, lang)
        return await self.peak(user_id, peak_id)

    async def add_peak(self, user_id: int, name: str, lat: float, lon: float, ele: float) -> Peak:
        cur = await self.conn.execute(
            "INSERT INTO peaks (user_id, name, lat, lon, ele) VALUES (?, ?, ?, ?, ?)",
            (user_id, name[:64], lat, lon, round(ele)),
        )
        await self.conn.commit()
        return Peak(cur.lastrowid, name[:64], lat, lon, round(ele))

    async def update_peak(self, user_id: int, peak_id: int, **fields) -> Peak | None:
        unknown = fields.keys() - {"name", "ele"}
        if unknown:
            raise ValueError(f"Неизвестные поля: {unknown}")
        assignments = ", ".join(f"{k} = ?" for k in fields)
        await self.conn.execute(
            f"UPDATE peaks SET {assignments} WHERE user_id = ? AND id = ?", (*fields.values(), user_id, peak_id)
        )
        await self.conn.commit()
        return await self.peak(user_id, peak_id)

    async def delete_peak(self, user_id: int, peak_id: int) -> None:
        await self.conn.execute("DELETE FROM peaks WHERE user_id = ? AND id = ?", (user_id, peak_id))
        await self.conn.commit()

    # ── общий каталог ──

    def _catalog_peak(self, row: aiosqlite.Row, lang: str) -> Peak:
        return Peak(
            id=-row["id"],
            name=row[NAME_COLUMNS.get(lang, "name_ru")] or row["name_ru"],
            lat=row["lat"],
            lon=row["lon"],
            ele=row["ele"],
            region=row["region"],
            author_id=row["author_id"],
        )

    async def seed_catalog(self, peaks: list[tuple]) -> None:
        await self.conn.executemany(
            """
            INSERT INTO catalog (slug, region, name_ru, name_uz, name_en, lat, lon, ele, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'approved')
            ON CONFLICT(slug) DO UPDATE SET
                region = excluded.region, name_ru = excluded.name_ru, name_uz = excluded.name_uz,
                name_en = excluded.name_en, lat = excluded.lat, lon = excluded.lon, ele = excluded.ele
            """,
            peaks,
        )
        await self.conn.commit()

    async def catalog(self, lang: str) -> list[Peak]:
        async with self.conn.execute("SELECT * FROM catalog WHERE status = 'approved'") as cur:
            return [self._catalog_peak(row, lang) for row in await cur.fetchall()]

    async def catalog_peak(self, catalog_id: int, lang: str) -> Peak | None:
        async with self.conn.execute(
            "SELECT * FROM catalog WHERE id = ? AND status = 'approved'", (catalog_id,)
        ) as cur:
            row = await cur.fetchone()
        return self._catalog_peak(row, lang) if row else None

    async def catalog_nearby(self, lat: float, lon: float, radius_deg: float = 0.004) -> list[aiosqlite.Row]:
        """Опубликованные и ожидающие проверки вершины рядом с точкой (~400 м) — для поиска дублей."""
        async with self.conn.execute(
            "SELECT * FROM catalog WHERE status IN ('approved', 'pending') "
            "AND abs(lat - ?) < ? AND abs(lon - ?) < ?",
            (lat, radius_deg, lon, radius_deg),
        ) as cur:
            return list(await cur.fetchall())

    async def submit_peak(self, user_id: int, peak: Peak) -> int:
        """Заявка на публикацию личной вершины. Возвращает id заявки в каталоге."""
        cur = await self.conn.execute(
            "INSERT INTO catalog (name_ru, name_uz, name_en, lat, lon, ele, status, author_id, source_peak_id) "
            "VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)",
            (peak.name, peak.name, peak.name, peak.lat, peak.lon, peak.ele, user_id, peak.id),
        )
        await self.conn.execute(
            "UPDATE peaks SET catalog_id = ? WHERE user_id = ? AND id = ?", (cur.lastrowid, user_id, peak.id)
        )
        await self.conn.commit()
        return cur.lastrowid

    async def cancel_request(self, request_id: int) -> None:
        await self.conn.execute("UPDATE peaks SET catalog_id = NULL WHERE catalog_id = ?", (request_id,))
        await self.conn.execute("DELETE FROM catalog WHERE id = ? AND status = 'pending'", (request_id,))
        await self.conn.commit()

    async def request(self, request_id: int) -> aiosqlite.Row | None:
        async with self.conn.execute("SELECT * FROM catalog WHERE id = ?", (request_id,)) as cur:
            return await cur.fetchone()

    async def pending_requests(self) -> list[aiosqlite.Row]:
        async with self.conn.execute("SELECT * FROM catalog WHERE status = 'pending' ORDER BY id") as cur:
            return list(await cur.fetchall())

    async def review(self, request_id: int, approved: bool, reviewer_id: int) -> aiosqlite.Row | None:
        """Решение админа. None — если заявка уже рассмотрена или не найдена."""
        cur = await self.conn.execute(
            "UPDATE catalog SET status = ?, reviewer_id = ?, reviewed_at = CURRENT_TIMESTAMP "
            "WHERE id = ? AND status = 'pending'",
            ("approved" if approved else "rejected", reviewer_id, request_id),
        )
        await self.conn.commit()
        return await self.request(request_id) if cur.rowcount else None
