import handlers
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from data import config
from loader import dp, db, bot
import filters

from logger import Logger

from database.setup import setup_db

setup_db()

filters.setup(dp)

user_message = 'Пользователь'



@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    message.bot.logger.user_id = message.from_user.id
    message.bot.logger.log_info(content="Зашел в бота")

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(user_message)

    value = db.fetchone(
        'SELECT * FROM "wallet" WHERE uid = ?',
        (message.from_user.id,)
    )

    if not value:
        db.query(
            'INSERT INTO "wallet" (cid, balance, uid) VALUES (?, ?, ?)',
            (message.chat.id, 0, message.from_user.id)
        )

    await message.answer(
        '''Привет! 👋

🤖 Я бот-магазин по продаже товаров любой категории.

🛍️ Чтобы перейти в каталог и выбрать приглянувшиеся товары воспользуйтесь командой /menu.

💰 Пополнить счет можно через Каспи или Qiwi.

❓ Возникли вопросы? Не проблема! Команда /sos поможет связаться с админами, которые постараются как можно быстрее откликнуться.

🤝 Нашли проблему? Свяжитесь с разработчиком <a href="https://t.me/Kllasret">Yan Krivolapov</a>
''',
        reply_markup=markup
    )


@dp.message_handler(text=user_message)
async def user_mode(message: types.Message):
    cid = message.chat.id
    if cid in config.ADMINS:
        config.ADMINS.remove(cid)

    await message.answer(
        'Вы вошли как пользователь, добро пожаловать!',
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message_handler(commands='admin')
async def admin_mode(message: types.Message):
    cid = message.chat.id
    if cid not in config.ADMINS:
        config.ADMINS.append(cid)

    await message.answer(
        'Включен админский режим.',
        reply_markup=ReplyKeyboardRemove()
    )


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