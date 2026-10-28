from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import screens, ui
from bot.db import Database
from bot.services import WeatherService

router = Router(name="commands")


async def _open(screen: str, message: Message, bot: Bot, state: FSMContext, db: Database, weather: WeatherService) -> None:
    """Команда открывает экран новым сообщением внизу чата, старое меню удаляется."""
    chat_id = message.chat.id
    await ui.delete_incoming(message)
    await ui.leave_location_mode(bot, state, chat_id)
    user = await db.get_user(chat_id)
    text, markup = await screens.build(screen, user, weather, name=message.from_user.first_name)
    await ui.send_fresh(bot, db, chat_id, text, markup)
    if screen == "location":
        await ui.enter_location_mode(bot, state, chat_id, user.lang)


@router.message(CommandStart())
@router.message(Command("weather"))
async def cmd_start(message: Message, bot: Bot, state: FSMContext, db: Database, weather: WeatherService) -> None:
    await _open("home", message, bot, state, db, weather)


@router.message(Command("location"))
async def cmd_location(message: Message, bot: Bot, state: FSMContext, db: Database, weather: WeatherService) -> None:
    await _open("location", message, bot, state, db, weather)


@router.message(Command("settings"))
async def cmd_settings(message: Message, bot: Bot, state: FSMContext, db: Database, weather: WeatherService) -> None:
    await _open("settings", message, bot, state, db, weather)


@router.message(Command("language", "lang"))
async def cmd_language(message: Message, bot: Bot, state: FSMContext, db: Database, weather: WeatherService) -> None:
    await _open("lang", message, bot, state, db, weather)
