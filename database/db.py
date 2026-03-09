import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL не найден. Добавь его в Railway Variables")

    conn = psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )

    return conn