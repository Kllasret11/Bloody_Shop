from hashlib import md5

from aiogram.dispatcher import FSMContext
from aiogram.types import (
    CallbackQuery,
    ContentType,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.types.chat import ChatActions
from aiogram.utils.callback_data import CallbackData

from data.config import ADMINS
from filters import IsAdmin
from handlers.user.menu import add_money, settings
from keyboards.default.markups import *
from loader import bot, db, dp
from states import AdminBalanceState, AdminPriceState, CategoryState, ProductState

category_cb = CallbackData('category', 'id', 'action')
product_cb = CallbackData('product', 'id', 'action')

add_product = '➕ Добавить товар'
delete_category = '🗑️ Удалить категорию'


@dp.message_handler(IsAdmin(), commands='notification')
async def test(message: Message):
    text = " ".join(message.text.split(' ')[1:])
    if len(text) == 0:
        return await message.answer('Вам нужно указать текст')

    data = db.fetchall('SELECT cid, uid FROM wallet')
    for chat_id, user_id in data:
        if user_id in ADMINS:
            continue
        await bot.send_message(chat_id, text.capitalize())

    await message.answer('Успешно отправлены сообщения')


@dp.message_handler(IsAdmin(), text=settings)
async def process_settings(message: Message):
    markup = InlineKeyboardMarkup()

    for idx, title in db.fetchall('SELECT * FROM categories ORDER BY title'):
        markup.add(InlineKeyboardButton(
            title, callback_data=category_cb.new(id=idx, action='view')))

    markup.add(InlineKeyboardButton(
        '+ Добавить категорию', callback_data='add_category'))

    await message.answer('Настройка категорий:', reply_markup=markup)


@dp.callback_query_handler(IsAdmin(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    category_idx = callback_data['id']

    products = db.fetchall(
        '''SELECT * FROM products product
           WHERE product.tag = (SELECT title FROM categories WHERE idx=?)
           ORDER BY title''',
        (category_idx,),
    )

    await query.message.delete()
    await query.answer('Все добавленные товары в эту категорию.')
    await state.update_data(category_index=category_idx)
    await show_products(query.message, products, category_idx)


@dp.callback_query_handler(IsAdmin(), text='add_category')
async def add_category_callback_handler(query: CallbackQuery):
    await query.message.delete()
    await query.message.answer('Название категории?')
    await CategoryState.title.set()


@dp.message_handler(IsAdmin(), state=CategoryState.title)
async def set_category_title_handler(message: Message, state: FSMContext):
    category = message.text.strip()
    idx = md5(category.encode('utf-8')).hexdigest()
    db.query(
        '''INSERT INTO categories VALUES (?, ?)
           ON CONFLICT (idx) DO UPDATE SET title = EXCLUDED.title''',
        (idx, category),
    )

    await state.finish()
    await process_settings(message)


@dp.message_handler(IsAdmin(), text=delete_category)
async def delete_category_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if 'category_index' in data.keys():
            idx = data['category_index']

            db.query(
                'DELETE FROM products WHERE tag IN (SELECT title FROM categories WHERE idx=?)', (idx,))
            db.query('DELETE FROM categories WHERE idx=?', (idx,))

            await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())
            await process_settings(message)


@dp.message_handler(IsAdmin(), text=add_product)
async def process_add_product(message: Message):
    await ProductState.title.set()

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_message)

    await message.answer('Название?', reply_markup=markup)


@dp.message_handler(IsAdmin(), text=cancel_message, state=ProductState.title)
async def process_cancel(message: Message, state: FSMContext):
    await message.answer('Ок, отменено!', reply_markup=ReplyKeyboardRemove())
    await state.finish()

    await process_settings(message)


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.title)
async def process_title_back(message: Message, state: FSMContext):
    await process_add_product(message)


@dp.message_handler(IsAdmin(), state=ProductState.title)
async def process_title(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text

    await ProductState.next()
    await message.answer('Описание?', reply_markup=back_markup())


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.body)
async def process_body_back(message: Message, state: FSMContext):
    await ProductState.title.set()

    async with state.proxy() as data:
        await message.answer(f"Изменить название с <b>{data['title']}</b>?", reply_markup=back_markup())


@dp.message_handler(IsAdmin(), state=ProductState.body)
async def process_body(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['body'] = message.text

    await ProductState.next()
    await message.answer('Фото?', reply_markup=back_markup())


@dp.message_handler(IsAdmin(), content_types=ContentType.PHOTO, state=ProductState.image)
async def process_image_photo(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = (await bot.download_file(file_info.file_path)).read()

    async with state.proxy() as data:
        data['image'] = downloaded_file

    await ProductState.next()
    await message.answer('Цена?', reply_markup=back_markup())


@dp.message_handler(IsAdmin(), content_types=ContentType.TEXT, state=ProductState.image)
async def process_image_url(message: Message, state: FSMContext):
    if message.text == back_message:
        await ProductState.body.set()

        async with state.proxy() as data:
            await message.answer(f"Изменить описание с <b>{data['body']}</b>?", reply_markup=back_markup())
    else:
        await message.answer('Вам нужно прислать фото товара.')


@dp.message_handler(IsAdmin(), lambda message: not message.text.isdigit(), state=ProductState.price)
async def process_price_invalid(message: Message, state: FSMContext):
    if message.text == back_message:
        await ProductState.image.set()

        async with state.proxy() as data:
            await message.answer('Другое изображение?', reply_markup=back_markup())
    else:
        await message.answer('Укажите цену в виде числа!')


@dp.message_handler(IsAdmin(), lambda message: message.text.isdigit(), state=ProductState.price)
async def process_price(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text

        title = data['title']
        body = data['body']
        price = data['price']

        await ProductState.next()
        text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price} тенге.'

        markup = check_markup()

        await message.answer_photo(photo=data['image'],
                                   caption=text,
                                   reply_markup=markup)


@dp.message_handler(IsAdmin(), lambda message: message.text not in [back_message, all_right_message],
                    state=ProductState.confirm)
async def process_confirm_invalid(message: Message, state: FSMContext):
    await message.answer('Такого варианта не было.')


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.confirm)
async def process_confirm_back(message: Message, state: FSMContext):
    await ProductState.price.set()

    async with state.proxy() as data:
        await message.answer(f"Изменить цену с <b>{data['price']}</b>?", reply_markup=back_markup())


@dp.message_handler(IsAdmin(), text=all_right_message, state=ProductState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    async with state.proxy() as data:
        title = data['title']
        body = data['body']
        image = data['image']
        price = data['price']

        tag = db.fetchone('SELECT title FROM categories WHERE idx=?', (data['category_index'],))[0]
        idx = md5(' '.join([title, body, price, tag]).encode('utf-8')).hexdigest()

        db.query('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)',
                 (idx, title, body, image, int(price), tag))

    await state.finish()
    await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())
    await process_settings(message)


@dp.callback_query_handler(IsAdmin(), product_cb.filter(action='delete'))
async def delete_product_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    product_idx = callback_data['id']
    db.query('DELETE FROM products WHERE idx=?', (product_idx,))
    await query.answer('Удалено!')
    await query.message.delete()


@dp.callback_query_handler(IsAdmin(), product_cb.filter(action='edit_price'))
async def edit_price_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    product_idx = callback_data['id']
    product = db.fetchone('SELECT title, price FROM products WHERE idx=?', (product_idx,))
    if not product:
        return await query.answer('Товар не найден.', show_alert=True)

    title, price = product
    await state.update_data(edit_product_idx=product_idx)
    await AdminPriceState.price.set()
    await query.message.answer(
        f'Введите новую цену для товара <b>{title}</b>.\nТекущая цена: <b>{price}₸</b>',
        reply_markup=back_markup(),
    )
    await query.answer()


@dp.message_handler(IsAdmin(), text=add_money)
async def add_money_start(message: Message):
    await AdminBalanceState.user_id.set()
    await message.answer('Введите Telegram ID пользователя, которому нужно пополнить баланс.', reply_markup=back_markup())


@dp.message_handler(IsAdmin(), state=AdminBalanceState.user_id)
async def add_money_user_id(message: Message, state: FSMContext):
    if message.text == back_message:
        await state.finish()
        return await message.answer('Отменено.', reply_markup=ReplyKeyboardRemove())

    if not message.text.isdigit():
        return await message.answer('ID должен состоять только из цифр.')

    await state.update_data(target_user_id=int(message.text))
    await AdminBalanceState.amount.set()
    await message.answer('Введите сумму пополнения в тенге.', reply_markup=back_markup())


@dp.message_handler(IsAdmin(), state=AdminBalanceState.amount)
async def add_money_amount(message: Message, state: FSMContext):
    if message.text == back_message:
        await AdminBalanceState.user_id.set()
        return await message.answer('Введите Telegram ID пользователя.', reply_markup=back_markup())

    normalized = message.text.replace(',', '.').strip()
    try:
        amount = float(normalized)
    except ValueError:
        return await message.answer('Введите корректную сумму числом.')

    if amount <= 0:
        return await message.answer('Сумма должна быть больше нуля.')

    data = await state.get_data()
    target_user_id = int(data['target_user_id'])
    current_wallet = db.fetchone('SELECT cid FROM wallet WHERE uid=?', (target_user_id,))
    cid = current_wallet[0] if current_wallet else target_user_id
    new_balance = db.add_balance(cid, target_user_id, amount)

    await state.finish()
    await message.answer(
        f'Баланс пользователя <b>{target_user_id}</b> пополнен на <b>{amount:.0f}₸</b>.\n'
        f'Новый баланс: <b>{new_balance:.0f}₸</b>',
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message_handler(IsAdmin(), state=AdminPriceState.price)
async def update_product_price(message: Message, state: FSMContext):
    if message.text == back_message:
        await state.finish()
        return await message.answer('Изменение цены отменено.', reply_markup=ReplyKeyboardRemove())

    if not message.text.isdigit():
        return await message.answer('Цена должна быть указана целым числом.')

    data = await state.get_data()
    product_idx = data.get('edit_product_idx')
    if not product_idx:
        await state.finish()
        return await message.answer('Не удалось определить товар.')

    new_price = int(message.text)
    db.query('UPDATE products SET price=? WHERE idx=?', (new_price, product_idx))
    product = db.fetchone('SELECT title FROM products WHERE idx=?', (product_idx,))
    await state.finish()
    await message.answer(
        f'Цена товара <b>{product[0] if product else product_idx}</b> изменена на <b>{new_price}₸</b>.',
        reply_markup=ReplyKeyboardRemove(),
    )


async def show_products(m, products, category_idx):
    await bot.send_chat_action(m.chat.id, ChatActions.TYPING)

    for idx, title, body, image, price, tag in products:
        text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price} тенге.'

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton('💵 Изменить цену', callback_data=product_cb.new(id=idx, action='edit_price')),
            InlineKeyboardButton('🗑️ Удалить', callback_data=product_cb.new(id=idx, action='delete')),
        )

        await m.answer_photo(photo=image,
                             caption=text,
                             reply_markup=markup)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(add_product)
    markup.add(delete_category)

    await m.answer('Хотите что-нибудь добавить или удалить?', reply_markup=markup)
