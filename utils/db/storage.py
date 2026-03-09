from __future__ import annotations

import os
from typing import Any, Iterable

import psycopg2
from psycopg2.extensions import connection as PGConnection


class DatabaseManager:
    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or os.getenv("DATABASE_URL", "").strip()
        if not self.dsn:
            raise RuntimeError("DATABASE_URL не задан. Добавь PostgreSQL в Railway и переменную DATABASE_URL.")

    def _connect(self) -> PGConnection:
        conn = psycopg2.connect(self.dsn)
        conn.autocommit = True
        return conn

    @staticmethod
    def _prepare_query(query: str) -> str:
        return query.replace("?", "%s")

    def create_tables(self) -> None:
        statements = [
            """
            CREATE TABLE IF NOT EXISTS categories (
                idx TEXT PRIMARY KEY,
                title TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS products (
                idx TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                photo BYTEA,
                price INTEGER NOT NULL,
                tag TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS orders (
                cid BIGINT NOT NULL,
                usr_name TEXT NOT NULL,
                usr_address TEXT NOT NULL,
                products TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS cart (
                cid BIGINT NOT NULL,
                idx TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (cid, idx)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS wallet (
                cid BIGINT NOT NULL,
                balance DOUBLE PRECISION NOT NULL DEFAULT 0,
                uid BIGINT PRIMARY KEY
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS questions (
                cid BIGINT PRIMARY KEY,
                question TEXT NOT NULL
            )
            """,
        ]
        with self._connect() as conn:
            with conn.cursor() as cur:
                for statement in statements:
                    cur.execute(statement)

    def query(self, arg: str, values: Iterable[Any] | None = None) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(self._prepare_query(arg), values)

    def fetchone(self, arg: str, values: Iterable[Any] | None = None):
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(self._prepare_query(arg), values)
                row = cur.fetchone()
                return self._normalize_row(row)

    def fetchall(self, arg: str, values: Iterable[Any] | None = None):
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(self._prepare_query(arg), values)
                rows = cur.fetchall()
                return [self._normalize_row(row) for row in rows]

    def _normalize_row(self, row):
        if row is None:
            return None
        return tuple(self._normalize_value(value) for value in row)

    @staticmethod
    def _normalize_value(value):
        if isinstance(value, memoryview):
            return value.tobytes()
        return value
