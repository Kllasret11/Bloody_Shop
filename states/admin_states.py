from aiogram.fsm.state import State, StatesGroup


class AdminBalanceState(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_amount = State()


class AdminPriceState(StatesGroup):
    waiting_for_product_id = State()
    waiting_for_price = State()