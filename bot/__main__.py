import asyncio
import contextlib
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatType, ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot import handlers, locales, scheduler
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

    bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(
        storage=storage, db=db, weather=weather, mountains=MountainService(weather), admins=config.admin_ids,
    )
    dp.message.filter(F.chat.type == ChatType.PRIVATE)
    dp.message.outer_middleware(UserMiddleware(db))
    dp.callback_query.outer_middleware(UserMiddleware(db))
    dp.include_routers(*handlers.routers())

    await set_commands(bot)
    logging.info("Качество воздуха: %s", "IQAir + Open-Meteo" if config.iqair_key else "Open-Meteo (CAMS)")
    if not config.admin_ids:
        logging.warning("ADMIN_IDS не задан — публикация вершин пользователей в каталог отключена")

    scheduler_task = asyncio.create_task(scheduler.run(bot, db, weather, storage))
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await scheduler_task
        await weather.close()
        await db.close()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
