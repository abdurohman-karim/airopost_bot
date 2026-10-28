import asyncio
import contextlib
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatType, ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot import handlers, scheduler
from bot.config import load_config
from bot.db import Database
from bot.services import WeatherService

COMMANDS = [
    BotCommand(command="start", description="🌤 Погода сейчас"),
    BotCommand(command="location", description="📍 Сменить местность"),
    BotCommand(command="settings", description="⚙️ Настройки и время сводки"),
]


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    config = load_config()

    db = Database(config.db_path, config.default_time)
    await db.connect()
    weather = WeatherService(iqair_key=config.iqair_key)
    await weather.start()

    bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage, db=db, weather=weather)
    dp.message.filter(F.chat.type == ChatType.PRIVATE)
    dp.include_routers(*handlers.routers())

    await bot.set_my_commands(COMMANDS)
    logging.info("Качество воздуха: %s", "IQAir + Open-Meteo" if config.iqair_key else "Open-Meteo (CAMS)")

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
