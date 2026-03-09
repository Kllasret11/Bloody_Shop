from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from loader import db


class IsUser(BoundFilter):
    async def check(self, message: Message):
        return not db.is_admin_session_active(message.from_user.id)
