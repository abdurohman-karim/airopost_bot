from aiogram import Router

from bot.handlers import admin, commands, fallback, inline, location, mountains, navigation, places, reports, routes, schedule, spots, trips, widgets


def routers() -> list[Router]:
    # mountains — раньше location: геопозиция в горных режимах относится к вершине, а не к городу.
    # fallback — последним: он удаляет всё, что не обработали остальные.
    return [
        commands.router, inline.router, widgets.router, admin.router, navigation.router, schedule.router,
        reports.router, places.router, routes.router, spots.router, trips.router, mountains.router, location.router, fallback.router,
    ]
