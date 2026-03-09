from aiogram.dispatcher.filters.state import State, StatesGroup


class CheckoutState(StatesGroup):
    name = State()
    address = State()
    confirm = State()
