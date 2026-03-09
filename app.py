import handlers
from aiogram import executor, types

import filters
from data import config
from keyboards.default.markups import user_menu_markup
from loader import bot, db, dp
from logger import Logger


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    db.ensure_wallet(message.from_user.id, message.chat.id)
    await message.answer(
        f'Привет! 👋\n\nДобро пожаловать в <b>{config.SHOP_TITLE}</b>.\n'
        'Открой /menu, чтобы посмотреть каталог, корзину и баланс.\n\n'
        'Для входа в админку используй /admin',
        reply_markup=user_menu_markup(),
    )


async def on_startup(_dp):
    db.create_tables()
    bot.logger = Logger()
    filters.setup(dp)


async def on_shutdown(_dp):
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
