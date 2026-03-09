from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup

from filters import IsUser
from keyboards.default.markups import back_message, confirm_message, confirm_order_markup, user_menu_markup
from keyboards.inline.store import cart_item_markup
from loader import dp, db
from states import CheckoutState


def _cart_rows(user_id: int):
    return db.fetchall(
        '''
        SELECT p.id, p.title, p.description, p.photo_file_id, p.price, c.quantity
        FROM cart_items c
        JOIN products p ON p.id = c.product_id
        WHERE c.user_id = ? AND p.is_active = TRUE
        ORDER BY p.id DESC
        ''',
        (user_id,),
    )


def _cart_total(rows) -> float:
    return sum(float(price) * int(quantity) for _, _, _, _, price, quantity in rows)


@dp.message_handler(IsUser(), text='🛒 Корзина')
async def show_cart(message: Message):
    rows = _cart_rows(message.from_user.id)
    if not rows:
        await message.answer('Корзина пуста.')
        return
    for product_id, title, description, photo_file_id, price, quantity in rows:
        text = f'<b>{title}</b>\n{description}\n\nЦена: {float(price):.2f}₸\nКоличество: {quantity}'
        if photo_file_id:
            await message.answer_photo(photo_file_id, caption=text, reply_markup=cart_item_markup(product_id, quantity))
        else:
            await message.answer(text, reply_markup=cart_item_markup(product_id, quantity))
    total = _cart_total(rows)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('📦 Оформить заказ')
    markup.row('🛍️ Каталог', '💰 Баланс')
    await message.answer(f'Итого: <b>{total:.2f}₸</b>', reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data == 'noop')
async def noop(query: CallbackQuery):
    await query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('cartinc:'))
async def cart_increase(query: CallbackQuery):
    product_id = int(query.data.split(':')[1])
    db.execute('UPDATE cart_items SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?', (query.from_user.id, product_id))
    row = db.fetchone('SELECT quantity FROM cart_items WHERE user_id = ? AND product_id = ?', (query.from_user.id, product_id))
    if row:
        await query.message.edit_reply_markup(cart_item_markup(product_id, int(row[0])))
    await query.answer('Количество увеличено.')


@dp.callback_query_handler(lambda c: c.data.startswith('cartdec:'))
async def cart_decrease(query: CallbackQuery):
    product_id = int(query.data.split(':')[1])
    row = db.fetchone('SELECT quantity FROM cart_items WHERE user_id = ? AND product_id = ?', (query.from_user.id, product_id))
    if not row:
        await query.answer()
        return
    quantity = int(row[0]) - 1
    if quantity <= 0:
        db.execute('DELETE FROM cart_items WHERE user_id = ? AND product_id = ?', (query.from_user.id, product_id))
        await query.message.delete()
    else:
        db.execute('UPDATE cart_items SET quantity = ? WHERE user_id = ? AND product_id = ?', (quantity, query.from_user.id, product_id))
        await query.message.edit_reply_markup(cart_item_markup(product_id, quantity))
    await query.answer('Корзина обновлена.')


@dp.callback_query_handler(lambda c: c.data.startswith('cartdel:'))
async def cart_delete(query: CallbackQuery):
    product_id = int(query.data.split(':')[1])
    db.execute('DELETE FROM cart_items WHERE user_id = ? AND product_id = ?', (query.from_user.id, product_id))
    await query.message.delete()
    await query.answer('Товар удалён.')


@dp.message_handler(IsUser(), text='📦 Оформить заказ')
async def checkout_start(message: Message):
    rows = _cart_rows(message.from_user.id)
    if not rows:
        await message.answer('Корзина пуста.')
        return
    total = _cart_total(rows)
    balance = db.get_balance(message.from_user.id)
    if balance < total:
        await message.answer(
            f'Недостаточно баланса.\nНужно: <b>{total:.2f}₸</b>\nНа счёте: <b>{balance:.2f}₸</b>'
        )
        return
    await CheckoutState.name.set()
    await message.answer(f'Сумма заказа: <b>{total:.2f}₸</b>\nВведите имя получателя.')


@dp.message_handler(IsUser(), state=CheckoutState.name)
async def checkout_name(message: Message, state: FSMContext):
    await state.update_data(customer_name=message.text.strip())
    await CheckoutState.address.set()
    await message.answer('Введите адрес доставки.')


@dp.message_handler(IsUser(), state=CheckoutState.address)
async def checkout_address(message: Message, state: FSMContext):
    await state.update_data(customer_address=message.text.strip())
    await CheckoutState.confirm.set()
    await message.answer('Подтвердить заказ?', reply_markup=confirm_order_markup())


@dp.message_handler(IsUser(), state=CheckoutState.confirm)
async def checkout_confirm(message: Message, state: FSMContext):
    if message.text == back_message:
        await CheckoutState.address.set()
        await message.answer('Введите адрес заново.')
        return
    if message.text != confirm_message:
        await message.answer('Нажмите кнопку подтверждения или назад.')
        return

    rows = _cart_rows(message.from_user.id)
    if not rows:
        await state.finish()
        await message.answer('Корзина пуста.', reply_markup=user_menu_markup())
        return

    total = _cart_total(rows)
    balance = db.get_balance(message.from_user.id)
    if balance < total:
        await state.finish()
        await message.answer(
            f'Недостаточно баланса.\nНужно: <b>{total:.2f}₸</b>\nНа счёте: <b>{balance:.2f}₸</b>',
            reply_markup=user_menu_markup(),
        )
        return

    data = await state.get_data()
    db.execute('UPDATE wallets SET balance = balance - ?, updated_at = NOW() WHERE user_id = ?', (total, message.from_user.id))
    db.execute(
        '''
        INSERT INTO orders (user_id, chat_id, customer_name, customer_address, total_amount)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (message.from_user.id, message.chat.id, data['customer_name'], data['customer_address'], total),
    )
    order_row = db.fetchone('SELECT id FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (message.from_user.id,))
    order_id = int(order_row[0])
    for product_id, title, _description, _photo, price, quantity in rows:
        db.execute(
            '''
            INSERT INTO order_items (order_id, product_id, title, price, quantity)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (order_id, product_id, title, float(price), int(quantity)),
        )
    db.execute('DELETE FROM cart_items WHERE user_id = ?', (message.from_user.id,))
    new_balance = db.get_balance(message.from_user.id)
    await state.finish()
    await message.answer(
        f'Заказ <b>#{order_id}</b> оформлен.\nСписано: <b>{total:.2f}₸</b>\nОстаток: <b>{new_balance:.2f}₸</b>',
        reply_markup=user_menu_markup(),
    )
