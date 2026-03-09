from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminAuthState(StatesGroup):
    login = State()
    password = State()
