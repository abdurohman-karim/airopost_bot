from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    location = State()      # ждём название города или геолокацию
    time = State()          # ждём время сводки текстом
    peak_search = State()   # ждём название вершины или точку на карте
    peak_edit = State()     # ждём высоту вершины числом или новое название
    peak_route = State()    # ждём текущую геопозицию на маршруте к вершине
    sos = State()           # экран SOS: ждём геопозицию, чтобы показать координаты для спасателей
