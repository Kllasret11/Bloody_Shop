from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterable, Iterator

import psycopg2
from psycopg2.extras import RealDictCursor


class DatabaseManager:
    def __init__(self, dsn: str):
        self.dsn = dsn

    @contextmanager
    def _connect(self) -> Iterator[psycopg2.extensions.connection]:
        conn = psycopg2.connect(self.dsn)
        conn.autocommit = True
        try:
            yield conn
        finally:
            conn.close()

    @staticmethod
    def _q(query: str) -> str:
        return query.replace('?', '%s')

    def execute(self, query: str, values: Iterable[Any] | None = None) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(self._q(query), values)

    def fetchone(self, query: str, values: Iterable[Any] | None = None):
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(self._q(query), values)
                return cur.fetchone()

    def fetchall(self, query: str, values: Iterable[Any] | None = None):
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(self._q(query), values)
                return cur.fetchall()

    def create_tables(self) -> None:
        statements = [
            '''
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL UNIQUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                photo_file_id TEXT,
                price NUMERIC(12,2) NOT NULL DEFAULT 0,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS wallets (
                user_id BIGINT PRIMARY KEY,
                chat_id BIGINT NOT NULL,
                balance NUMERIC(12,2) NOT NULL DEFAULT 0,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS cart_items (
                user_id BIGINT NOT NULL,
                product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                quantity INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (user_id, product_id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                chat_id BIGINT NOT NULL,
                customer_name TEXT NOT NULL,
                customer_address TEXT NOT NULL,
                total_amount NUMERIC(12,2) NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
                title TEXT NOT NULL,
                price NUMERIC(12,2) NOT NULL,
                quantity INTEGER NOT NULL
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS admin_sessions (
                user_id BIGINT PRIMARY KEY,
                is_active BOOLEAN NOT NULL DEFAULT FALSE,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS support_questions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                chat_id BIGINT NOT NULL,
                question TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            ''',
        ]
        for statement in statements:
            self.execute(statement)

    def ensure_wallet(self, user_id: int, chat_id: int) -> None:
        self.execute(
            '''
            INSERT INTO wallets (user_id, chat_id, balance)
            VALUES (?, ?, 0)
            ON CONFLICT (user_id)
            DO UPDATE SET chat_id = EXCLUDED.chat_id
            ''',
            (user_id, chat_id),
        )

    def get_balance(self, user_id: int) -> float:
        row = self.fetchone('SELECT balance FROM wallets WHERE user_id = ?', (user_id,))
        return float(row[0]) if row else 0.0

    def add_balance(self, user_id: int, chat_id: int, amount: float) -> float:
        self.ensure_wallet(user_id, chat_id)
        self.execute(
            '''
            UPDATE wallets
            SET balance = balance + ?, updated_at = NOW(), chat_id = ?
            WHERE user_id = ?
            ''',
            (amount, chat_id, user_id),
        )
        return self.get_balance(user_id)

    def set_balance(self, user_id: int, chat_id: int, amount: float) -> float:
        self.ensure_wallet(user_id, chat_id)
        self.execute(
            '''
            UPDATE wallets
            SET balance = ?, updated_at = NOW(), chat_id = ?
            WHERE user_id = ?
            ''',
            (amount, chat_id, user_id),
        )
        return self.get_balance(user_id)

    def activate_admin_session(self, user_id: int) -> None:
        self.execute(
            '''
            INSERT INTO admin_sessions (user_id, is_active)
            VALUES (?, TRUE)
            ON CONFLICT (user_id)
            DO UPDATE SET is_active = TRUE, updated_at = NOW()
            ''',
            (user_id,),
        )

    def deactivate_admin_session(self, user_id: int) -> None:
        self.execute(
            '''
            INSERT INTO admin_sessions (user_id, is_active)
            VALUES (?, FALSE)
            ON CONFLICT (user_id)
            DO UPDATE SET is_active = FALSE, updated_at = NOW()
            ''',
            (user_id,),
        )

    def is_admin_session_active(self, user_id: int) -> bool:
        row = self.fetchone('SELECT is_active FROM admin_sessions WHERE user_id = ?', (user_id,))
        return bool(row and row[0])
