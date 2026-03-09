from aiogram.dispatcher.filters.state import State, StatesGroup


class CategoryCreateState(StatesGroup):
    title = State()


class ProductCreateState(StatesGroup):
    category = State()
    title = State()
    description = State()
    photo = State()
    price = State()


class PriceEditState(StatesGroup):
    product_id = State()
    price = State()


class BalanceEditState(StatesGroup):
    user_id = State()
    amount = State()
