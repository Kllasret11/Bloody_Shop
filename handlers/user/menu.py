from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove
from loader import dp, db
from filters import IsAdmin, IsUser

catalog = '🛍️ Каталог'
balance = 'Профиль'
cart = '🛒 Корзина'
delivery_status = '🚚 Статус заказа'

settings = '⚙️ Настройка каталога'
orders = '🚚 Заказы'
questions = '❓ Вопросы'
add_money = '💸 Пополнить баланс'
logout_admin = '🔒 Выйти из админ-панели'


@dp.message_handler(IsAdmin(), commands='menu')
async def admin_menu(message: Message):
    message.bot.logger.user_id = message.from_user.id
    message.bot.logger.log_info(content="Вызвал меню")
    markup = ReplyKeyboardMarkup(selective=True, resize_keyboard=True)
    markup.add(settings)
    markup.add(add_money)
    markup.add(questions, orders)
    markup.add(logout_admin)

    await message.answer('Админ-панель', reply_markup=markup)


@dp.message_handler(IsAdmin(), text=logout_admin)
async def admin_logout(message: Message):
    db.deactivate_admin_session(message.from_user.id)
    await message.answer('Вы вышли из админ-панели.', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(IsUser(), commands='menu')
async def user_menu(message: Message):
    message.bot.logger.user_id = message.from_user.id
    message.bot.logger.log_info(content="Вызвал меню")
    markup = ReplyKeyboardMarkup(selective=True, resize_keyboard=True)
    markup.add(catalog)
    markup.add(balance, cart)
    markup.add(delivery_status)

    await message.answer('Меню', reply_markup=markup)
