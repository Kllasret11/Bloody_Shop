from aiogram import Dispatcher

from .is_admin import IsAdmin
from .is_user import IsUser


def setup(dp: Dispatcher):
    dp.filters_factory.bind(IsAdmin)
    dp.filters_factory.bind(IsUser)
