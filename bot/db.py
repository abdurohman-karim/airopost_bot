from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import aiosqlite

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
    created_at     TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

COLUMNS = {"lat", "lon", "place", "tz", "notify_time", "notify_enabled", "last_sent", "menu_msg_id"}


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
        )


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
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()

    @property
    def conn(self) -> aiosqlite.Connection:
        assert self._conn, "Database.connect() не вызван"
        return self._conn

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
