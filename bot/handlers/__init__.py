from aiogram import Router

from bot.handlers import admin, commands, fallback, location, mountains, navigation, places, routes, schedule, spots, trips


def routers() -> list[Router]:
    # mountains — раньше location: геопозиция в горных режимах относится к вершине, а не к городу.
    # fallback — последним: он удаляет всё, что не обработали остальные.
    return [
        commands.router, admin.router, navigation.router, schedule.router,
        places.router, routes.router, spots.router, trips.router, mountains.router, location.router, fallback.router,
    ]
