
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from loader import dp
from filters import IsAdmin, IsUser

catalog = '🛍️ Каталог'
balance = 'Профиль'
cart = '🛒 Корзина'
delivery_status = '🚚 Статус заказа'

settings = '⚙️ Настройка каталога'
orders = '🚚 Заказы'
questions = '❓ Вопросы'


@dp.message_handler(IsAdmin(), commands='menu')
async def admin_menu(message: Message):
    message.bot.logger.user_id = message.from_user.id
    message.bot.logger.log_info(content="Вызвал меню")
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(settings)
    markup.add(questions, orders)

    await message.answer('Меню', reply_markup=markup)


@dp.message_handler(IsUser(), commands='menu')
async def user_menu(message: Message):
    message.bot.logger.user_id = message.from_user.id
    message.bot.logger.log_info(content="Вызвал меню")
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(catalog)
    markup.add(balance, cart)
    markup.add(delivery_status)

    await message.answer('Меню', reply_markup=markup)
