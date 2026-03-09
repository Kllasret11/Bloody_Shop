from aiogram.types import CallbackQuery, Message

from filters import IsUser
from keyboards.inline.store import categories_markup, product_buy_markup, products_markup
from loader import dp, db


@dp.message_handler(IsUser(), text='🛍️ Каталог')
async def catalog_menu(message: Message):
    categories = db.fetchall('SELECT id, title FROM categories ORDER BY title')
    if not categories:
        await message.answer('Каталог пока пуст.')
        return
    await message.answer('Выберите категорию:', reply_markup=categories_markup(categories))


@dp.callback_query_handler(lambda c: c.data.startswith('cat:'))
async def category_open(query: CallbackQuery):
    category_id = int(query.data.split(':')[1])
    products = db.fetchall(
        'SELECT id, title, price FROM products WHERE category_id = ? AND is_active = TRUE ORDER BY id DESC',
        (category_id,),
    )
    if not products:
        await query.answer('В этой категории пока нет товаров.', show_alert=True)
        return
    await query.message.answer('Товары категории:', reply_markup=products_markup(products))
    await query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('prd:'))
async def product_open(query: CallbackQuery):
    product_id = int(query.data.split(':')[1])
    row = db.fetchone(
        'SELECT p.id, p.title, p.description, p.photo_file_id, p.price, c.title FROM products p LEFT JOIN categories c ON c.id = p.category_id WHERE p.id = ? AND p.is_active = TRUE',
        (product_id,),
    )
    if not row:
        await query.answer('Товар не найден.', show_alert=True)
        return
    _, title, description, photo_file_id, price, category_title = row
    caption = f'<b>{title}</b>\nКатегория: {category_title or "Без категории"}\n\n{description}\n\nЦена: <b>{float(price):.2f}₸</b>'
    if photo_file_id:
        await query.message.answer_photo(photo=photo_file_id, caption=caption, reply_markup=product_buy_markup(product_id))
    else:
        await query.message.answer(caption, reply_markup=product_buy_markup(product_id))
    await query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('addcart:'))
async def add_to_cart(query: CallbackQuery):
    product_id = int(query.data.split(':')[1])
    row = db.fetchone('SELECT id FROM products WHERE id = ? AND is_active = TRUE', (product_id,))
    if not row:
        await query.answer('Товар не найден.', show_alert=True)
        return
    db.execute(
        '''
        INSERT INTO cart_items (user_id, product_id, quantity)
        VALUES (?, ?, 1)
        ON CONFLICT (user_id, product_id)
        DO UPDATE SET quantity = cart_items.quantity + 1
        ''',
        (query.from_user.id, product_id),
    )
    await query.answer('Товар добавлен в корзину.')
