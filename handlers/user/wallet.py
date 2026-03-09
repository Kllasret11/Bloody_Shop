from __future__ import annotations

from pathlib import Path

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from filters import IsUser
from loader import dp, db

PROFILE_IMAGE_PATH = Path(__file__).resolve().parents[2] / "profile.jpg"


@dp.message_handler(IsUser(), text=balance)
async def process_balance(message: Message, state: FSMContext):
    message.bot.logger.user_id = message.from_user.id
    message.bot.logger.log_info(content='Посмотрел профиль')
    user_balance = db.fetchone('SELECT * FROM wallet WHERE uid = ?', (message.from_user.id,))

    with PROFILE_IMAGE_PATH.open('rb') as photo:
        await message.answer_photo(
            photo,
            f"""
    <b>📇 Твой профиль:</b>\n
    <b>👤 | Имя:</b> {message.from_user.first_name}
    <b>👤 | Ваш ID:</b> {message.from_user.id}
    <b>💸 | Баланс:</b> {user_balance[1] if user_balance else 0} ₸
    """,
            parse_mode='HTML'
        )
