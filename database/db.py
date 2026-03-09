from __future__ import annotations

import os

import psycopg2


def get_connection():
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError("DATABASE_URL не найден. Добавь PostgreSQL service в Railway Variables.")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    return conn
