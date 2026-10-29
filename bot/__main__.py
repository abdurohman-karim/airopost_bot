import asyncio
import contextlib
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatType, ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot import alerts, handlers, links, locales, scheduler
from bot.catalog import PEAKS
from bot.config import load_config
from bot.db import Database
from bot.middlewares import UserMiddleware
from bot.services import MountainService, WeatherService


async def set_commands(bot: Bot) -> None:
    """Меню команд на языке интерфейса Telegram; для остальных языков — английское."""
    for code in (None, *locales.LANGS):
        loc = locales.get(code or "en")
        commands = [
            BotCommand(command="start", description=loc["cmd_start"]),
            BotCommand(command="location", description=loc["cmd_location"]),
            BotCommand(command="settings", description=loc["cmd_settings"]),
            BotCommand(command="language", description=loc["cmd_language"]),
            BotCommand(command="sos", description=loc["cmd_sos"]),
        ]
        await bot.set_my_commands(commands, language_code=code)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    config = load_config()

    db = Database(config.db_path, config.default_time)
    await db.connect()
    await db.seed_catalog(PEAKS)
    weather = WeatherService(iqair_key=config.iqair_key)
    await weather.start()
    mountains = MountainService(weather)

    # Без превью ссылок: карта в SOS и ссылки в заявках не должны раздувать сообщения
    bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True))
    links.init((await bot.me()).username)
    storage = MemoryStorage()
    dp = Dispatcher(
        storage=storage, db=db, weather=weather, mountains=mountains, admins=config.admin_ids,
        backups=Path(config.db_path).parent / "backups",
    )
    dp.message.filter(F.chat.type == ChatType.PRIVATE)
    dp.message.outer_middleware(UserMiddleware(db))
    dp.callback_query.outer_middleware(UserMiddleware(db))
    dp.include_routers(*handlers.routers())

    await set_commands(bot)
    logging.info("Качество воздуха: %s", "IQAir + Open-Meteo" if config.iqair_key else "Open-Meteo (CAMS)")
    if not config.admin_ids:
        logging.warning("ADMIN_IDS не задан — публикация вершин пользователей в каталог отключена")

    tasks = [
        asyncio.create_task(scheduler.run(bot, db, weather, storage)),
        asyncio.create_task(alerts.run(bot, db, mountains, storage, dp["backups"])),
        asyncio.create_task(alerts.run_trips(bot, db)),
    ]
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        for task in tasks:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        await weather.close()
        await db.close()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
