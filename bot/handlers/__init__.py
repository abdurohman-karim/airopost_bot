from aiogram import Router

from bot.handlers import admin, commands, fallback, location, mountains, navigation, schedule


def routers() -> list[Router]:
    # mountains — раньше location: геопозиция в горных режимах относится к вершине, а не к городу.
    # fallback — последним: он удаляет всё, что не обработали остальные.
    return [
        commands.router, admin.router, navigation.router, schedule.router,
        mountains.router, location.router, fallback.router,
    ]
