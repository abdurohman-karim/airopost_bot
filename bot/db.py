from __future__ import annotations

import json
import secrets
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
    last_seen      TEXT,             -- UTC, последнее сообщение или нажатие
    digest_week    TEXT,             -- суббота выходных, прогноз на которые уже отправлен
    route_lat      REAL,             -- последняя точка с маршрута — для экрана SOS
    route_lon      REAL,
    route_ele      REAL,
    route_at       TEXT,             -- UTC, ISO
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
    share_token TEXT,                -- ссылка «Поделиться»: по ней вершину копируют себе
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS peaks_user ON peaks (user_id);

-- Подписки на прогноз выходных для вершин
CREATE TABLE IF NOT EXISTS peak_subs (
    user_id    INTEGER NOT NULL,
    peak_id    INTEGER NOT NULL,     -- > 0 личная вершина, < 0 вершина каталога (−id)
    snapshot   TEXT,                 -- JSON {дата: оценка}: что пользователю последний раз сообщили
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, peak_id)
);

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

COLUMNS = {
    "lat", "lon", "place", "tz", "notify_time", "notify_enabled", "last_sent", "menu_msg_id", "lang",
    "digest_week", "route_lat", "route_lon", "route_ele", "route_at",
}

# Колонки, добавленные после первой версии: (таблица, имя, тип) — для обновления старых баз
MIGRATIONS = [
    ("users", "lang", "TEXT"), ("peaks", "catalog_id", "INTEGER"),
    ("users", "last_seen", "TEXT"), ("users", "digest_week", "TEXT"),
    ("users", "route_lat", "REAL"), ("users", "route_lon", "REAL"), ("users", "route_ele", "REAL"),
    ("users", "route_at", "TEXT"), ("peaks", "share_token", "TEXT"),
]


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
    digest_week: str | None = None
    route_lat: float | None = None
    route_lon: float | None = None
    route_ele: float | None = None
    route_at: str | None = None

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
            digest_week=row["digest_week"],
            route_lat=row["route_lat"],
            route_lon=row["route_lon"],
            route_ele=row["route_ele"],
            route_at=row["route_at"],
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
    token: str | None = None     # личная: ключ ссылки «Поделиться»

    @property
    def public(self) -> bool:
        return self.id < 0

    @property
    def catalog_id(self) -> int:
        return -self.id


MAX_PEAKS = 10
MAX_SUBS = 5
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
        await self._conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS peaks_token ON peaks (share_token)")
        await self._conn.execute(
            "UPDATE peaks SET share_token = lower(hex(randomblob(6))) WHERE share_token IS NULL"
        )
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()

    @property
    def conn(self) -> aiosqlite.Connection:
        assert self._conn, "Database.connect() не вызван"
        return self._conn

    async def ensure_user(self, user_id: int, lang: str) -> None:
        """Создать пользователя при первом обращении, сразу с языком из Telegram, и отметить активность."""
        await self.conn.execute(
            "INSERT OR IGNORE INTO users (user_id, notify_time, lang) VALUES (?, ?, ?)",
            (user_id, self._default_time, lang),
        )
        await self.conn.execute("UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
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
        "SELECT p.id, p.user_id, p.name, p.lat, p.lon, p.ele, p.share_token, c.status "
        "FROM peaks p LEFT JOIN catalog c ON c.id = p.catalog_id "
    )

    @staticmethod
    def _peak(row: aiosqlite.Row) -> Peak:
        return Peak(
            id=row["id"], name=row["name"], lat=row["lat"], lon=row["lon"], ele=row["ele"],
            status=row["status"], token=row["share_token"],
        )

    async def peaks(self, user_id: int) -> list[Peak]:
        async with self.conn.execute(self._PEAK_SELECT + "WHERE p.user_id = ? ORDER BY p.id", (user_id,)) as cur:
            return [self._peak(row) for row in await cur.fetchall()]

    async def peak(self, user_id: int, peak_id: int) -> Peak | None:
        async with self.conn.execute(
            self._PEAK_SELECT + "WHERE p.user_id = ? AND p.id = ?", (user_id, peak_id)
        ) as cur:
            row = await cur.fetchone()
        return self._peak(row) if row else None

    async def shared_peak(self, token: str) -> tuple[int, Peak] | None:
        """Вершина по ссылке «Поделиться»: (владелец, вершина)."""
        async with self.conn.execute(self._PEAK_SELECT + "WHERE p.share_token = ?", (token,)) as cur:
            row = await cur.fetchone()
        return (row["user_id"], self._peak(row)) if row else None

    async def resolve_peak(self, user_id: int, peak_id: int, lang: str) -> Peak | None:
        """Вершина по id из кнопки: своя (id > 0) или из общего каталога (id < 0)."""
        if peak_id < 0:
            return await self.catalog_peak(-peak_id, lang)
        return await self.peak(user_id, peak_id)

    async def add_peak(self, user_id: int, name: str, lat: float, lon: float, ele: float) -> Peak:
        token = secrets.token_hex(6)
        cur = await self.conn.execute(
            "INSERT INTO peaks (user_id, name, lat, lon, ele, share_token) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, name[:64], lat, lon, round(ele), token),
        )
        await self.conn.commit()
        return Peak(cur.lastrowid, name[:64], lat, lon, round(ele), token=token)

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
        await self.conn.execute("DELETE FROM peak_subs WHERE user_id = ? AND peak_id = ?", (user_id, peak_id))
        await self.conn.commit()

    # ── подписки на прогноз выходных ──

    async def subscriptions(self, user_id: int) -> list[int]:
        async with self.conn.execute(
            "SELECT peak_id FROM peak_subs WHERE user_id = ? ORDER BY created_at", (user_id,)
        ) as cur:
            return [row["peak_id"] for row in await cur.fetchall()]

    async def all_subscriptions(self) -> dict[int, dict[int, dict]]:
        """{пользователь: {вершина: снимок}} — снимок: {дата: оценка}, о которой уже сообщили."""
        result: dict[int, dict[int, dict]] = {}
        async with self.conn.execute("SELECT * FROM peak_subs ORDER BY user_id, created_at") as cur:
            for row in await cur.fetchall():
                result.setdefault(row["user_id"], {})[row["peak_id"]] = json.loads(row["snapshot"] or "{}")
        return result

    async def subscribe(self, user_id: int, peak_id: int) -> None:
        await self.conn.execute("INSERT OR IGNORE INTO peak_subs (user_id, peak_id) VALUES (?, ?)", (user_id, peak_id))
        await self.conn.commit()

    async def unsubscribe(self, user_id: int, peak_id: int) -> None:
        await self.conn.execute("DELETE FROM peak_subs WHERE user_id = ? AND peak_id = ?", (user_id, peak_id))
        await self.conn.commit()

    async def set_snapshot(self, user_id: int, peak_id: int, snapshot: dict) -> None:
        await self.conn.execute(
            "UPDATE peak_subs SET snapshot = ? WHERE user_id = ? AND peak_id = ?",
            (json.dumps(snapshot), user_id, peak_id),
        )
        await self.conn.commit()

    # ── для админа ──

    async def stats(self) -> dict[str, int]:
        queries = {
            "users": "SELECT count(*) FROM users",
            "with_place": "SELECT count(*) FROM users WHERE lat IS NOT NULL",
            "notify": "SELECT count(*) FROM users WHERE notify_enabled = 1 AND lat IS NOT NULL",
            "new_7d": "SELECT count(*) FROM users WHERE created_at >= datetime('now', '-7 days')",
            "active_1d": "SELECT count(*) FROM users WHERE last_seen >= datetime('now', '-1 day')",
            "active_7d": "SELECT count(*) FROM users WHERE last_seen >= datetime('now', '-7 days')",
            "active_30d": "SELECT count(*) FROM users WHERE last_seen >= datetime('now', '-30 days')",
            "lang_ru": "SELECT count(*) FROM users WHERE coalesce(lang, 'ru') = 'ru'",
            "lang_uz": "SELECT count(*) FROM users WHERE lang = 'uz'",
            "lang_en": "SELECT count(*) FROM users WHERE lang = 'en'",
            "peaks": "SELECT count(*) FROM peaks",
            "peak_owners": "SELECT count(DISTINCT user_id) FROM peaks",
            "catalog": "SELECT count(*) FROM catalog WHERE status = 'approved'",
            "community": "SELECT count(*) FROM catalog WHERE status = 'approved' AND author_id IS NOT NULL",
            "pending": "SELECT count(*) FROM catalog WHERE status = 'pending'",
            "subs": "SELECT count(*) FROM peak_subs",
            "subscribers": "SELECT count(DISTINCT user_id) FROM peak_subs",
            "on_route_1d": "SELECT count(*) FROM users WHERE route_at >= datetime('now', '-1 day')",
        }
        result = {}
        for key, query in queries.items():
            async with self.conn.execute(query) as cur:
                result[key] = (await cur.fetchone())[0]
        return result

    async def backup(self, path: Path) -> None:
        """Согласованная копия базы одним файлом (работает и пока бот пишет в базу)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.unlink(missing_ok=True)
        await self.conn.execute("VACUUM INTO ?", (str(path),))

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
