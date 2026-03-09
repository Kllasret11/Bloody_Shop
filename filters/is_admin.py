from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from data.config import ADMINS
from loader import db


class IsAdmin(BoundFilter):
    async def check(self, message: Message):
        return message.from_user.id in ADMINS and db.is_admin_session_active(message.from_user.id)
