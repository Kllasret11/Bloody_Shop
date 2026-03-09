from __future__ import annotations

import os

BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
if not BOT_TOKEN:
    raise RuntimeError('BOT_TOKEN не задан. Добавь его в Railway Variables.')

DATABASE_URL = os.getenv('DATABASE_URL', '').strip()
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL не задан. Добавь PostgreSQL в Railway.')

ADMINS = [
    int(value.strip())
    for value in os.getenv('ADMINS', '').split(',')
    if value.strip()
]

ADMIN_LOGIN = os.getenv('ADMIN_LOGIN', 'Kllasret').strip()
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '123').strip()
SHOP_TITLE = os.getenv('SHOP_TITLE', 'Магазин')
CURRENCY = os.getenv('CURRENCY', '₸')
