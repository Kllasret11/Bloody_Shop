import handlers
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

import filters
from data import config
from loader import dp, db, bot
from logger import Logger
from states import AdminAuthState
from handlers.user.menu import admin_menu, user_menu

user_message = 'Пользователь'


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    message.bot.logger.user_id = message.from_user.id
    message.bot.logger.log_info(content="Зашел в бота")

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(user_message)

    db.ensure_wallet(message.chat.id, message.from_user.id)

    await message.answer(
        '''Привет! 👋

🤖 Я бот-магазин по продаже товаров любой категории.

🛍️ Чтобы перейти в каталог и выбрать приглянувшиеся товары воспользуйтесь командой /menu.

💰 Пополнить счет можно через админа.

❓ Возникли вопросы? Не проблема! Команда /sos поможет связаться с админами, которые постараются как можно быстрее откликнуться.

🤝 Нашли проблему? Свяжитесь с разработчиком <a href="https://t.me/Kllasret">Yan Krivolapov</a>
''',
        reply_markup=markup
    )


@dp.message_handler(text=user_message)
async def user_mode(message: types.Message):
    db.deactivate_admin_session(message.from_user.id)
    await message.answer(
        'Вы вошли как пользователь, добро пожаловать!',
        reply_markup=ReplyKeyboardRemove()
    )
    await user_menu(message)


@dp.message_handler(commands='admin')
async def admin_mode(message: types.Message):
    if message.from_user.id not in config.ADMINS:
        return await message.answer('У вас нет доступа к админ-панели.')

    await AdminAuthState.login.set()
    await message.answer('Введите логин администратора.', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=AdminAuthState.login)
async def admin_login_step(message: types.Message, state):
    await state.update_data(admin_login=message.text.strip())
    await AdminAuthState.password.set()
    await message.answer('Введите пароль администратора.')


@dp.message_handler(state=AdminAuthState.password)
async def admin_password_step(message: types.Message, state):
    data = await state.get_data()
    login = data.get('admin_login', '').strip()
    password = message.text.strip()

    if login == config.ADMIN_LOGIN and password == config.ADMIN_PASSWORD:
        db.activate_admin_session(message.from_user.id)
        await state.finish()
        await message.answer('Вход выполнен. Добро пожаловать в админ-панель.')
        await admin_menu(message)
    else:
        db.deactivate_admin_session(message.from_user.id)
        await state.finish()
        await message.answer('Неверный логин или пароль.')


async def on_startup(dp):
    db.create_tables()
    bot.logger = Logger()
    bot.logger.log_info(content='Бот запустился')


async def on_shutdown(dp):
    bot.logger.log_info(content='Бот выключился')
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )
