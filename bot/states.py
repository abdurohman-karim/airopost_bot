from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    location = State()   # ждём название города или геолокацию
    time = State()       # ждём время сводки текстом
