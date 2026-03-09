from aiogram.types import Message

from filters import IsUser
from keyboards.default.markups import user_menu_markup
from loader import dp, db


@dp.message_handler(IsUser(), commands='menu')
async def user_menu(message: Message):
    db.ensure_wallet(message.from_user.id, message.chat.id)
    await message.answer('Меню магазина', reply_markup=user_menu_markup())


@dp.message_handler(IsUser(), text='💰 Баланс')
async def show_balance(message: Message):
    db.ensure_wallet(message.from_user.id, message.chat.id)
    balance = db.get_balance(message.from_user.id)
    await message.answer(f'Ваш баланс: <b>{balance:.2f}₸</b>')


@dp.message_handler(IsUser(), text='🚚 Мои заказы')
async def show_orders(message: Message):
    rows = db.fetchall(
        'SELECT id, total_amount, status, created_at FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 10',
        (message.from_user.id,),
    )
    if not rows:
        await message.answer('У вас пока нет заказов.')
        return
    text = '\n\n'.join(
        f'Заказ #{order_id}\nСумма: {float(total):.2f}₸\nСтатус: {status}\nДата: {created_at:%Y-%m-%d %H:%M}'
        for order_id, total, status, created_at in rows
    )
    await message.answer(text)
