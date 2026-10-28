from aiogram import Router

from bot.handlers import commands, fallback, location, navigation, schedule


def routers() -> list[Router]:
    # fallback — последним: он удаляет всё, что не обработали остальные
    return [commands.router, navigation.router, schedule.router, location.router, fallback.router]
