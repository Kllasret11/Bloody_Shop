from aiogram.fsm.state import State, StatesGroup


class CategoryState(StatesGroup):
    waiting_for_category_name = State()


class ProductState(StatesGroup):
    waiting_for_product_name = State()
    waiting_for_price = State()
    waiting_for_category = State()