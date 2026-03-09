from __future__ import annotations

import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан. Добавь его в Railway Variables.")

ADMINS = [
    int(value.strip())
    for value in os.getenv("ADMINS", "1160081337").split(",")
    if value.strip()
]
