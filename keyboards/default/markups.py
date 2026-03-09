from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

back_message = '👈 Назад'
cancel_message = '🚫 Отменить'
confirm_message = '✅ Подтвердить заказ'
all_right_message = '✅ Все верно'


def user_menu_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton('🛍️ Каталог'))
    markup.row(KeyboardButton('💰 Баланс'), KeyboardButton('🛒 Корзина'))
    markup.row(KeyboardButton('🚚 Мои заказы'))
    return markup


def admin_menu_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton('📂 Категории'), KeyboardButton('➕ Товар'))
    markup.row(KeyboardButton('💳 Изменить цену'), KeyboardButton('💸 Пополнить баланс'))
    markup.row(KeyboardButton('📦 Заказы'), KeyboardButton('🔒 Выйти из админки'))
    return markup


def back_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(back_message)
    return markup


def cancel_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_message)
    return markup


def confirm_order_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(confirm_message, back_message)
    return markup
