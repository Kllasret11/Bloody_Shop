from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def categories_markup(categories):
    markup = InlineKeyboardMarkup(row_width=1)
    for category_id, title in categories:
        markup.add(InlineKeyboardButton(title, callback_data=f'cat:{category_id}'))
    return markup


def products_markup(products):
    markup = InlineKeyboardMarkup(row_width=1)
    for product_id, title, price in products:
        markup.add(InlineKeyboardButton(f'{title} — {price:.2f}₸', callback_data=f'prd:{product_id}'))
    return markup


def product_buy_markup(product_id: int):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('🛒 Добавить в корзину', callback_data=f'addcart:{product_id}'))
    return markup


def cart_item_markup(product_id: int, quantity: int):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton('➖', callback_data=f'cartdec:{product_id}'),
        InlineKeyboardButton(str(quantity), callback_data='noop'),
        InlineKeyboardButton('➕', callback_data=f'cartinc:{product_id}'),
    )
    markup.add(InlineKeyboardButton('🗑 Удалить', callback_data=f'cartdel:{product_id}'))
    return markup
