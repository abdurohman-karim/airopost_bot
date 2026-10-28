import os
import re
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str
    iqair_key: str | None
    db_path: str
    default_time: str


def load_config() -> Config:
    load_dotenv()
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN не задан — скопируйте .env.example в .env и впишите токен от @BotFather")

    default_time = os.getenv("DEFAULT_NOTIFY_TIME", "08:00").strip()
    if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", default_time):
        raise RuntimeError("DEFAULT_NOTIFY_TIME должен быть в формате ЧЧ:ММ, например 08:00")

    return Config(
        bot_token=token,
        iqair_key=os.getenv("IQAIR_API_KEY", "").strip() or None,
        db_path=os.getenv("DB_PATH", "data/bot.db").strip(),
        default_time=default_time,
    )
