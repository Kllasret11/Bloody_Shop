from __future__ import annotations

import sqlite3 as lite


class DatabaseManager:
    def __init__(self, path: str):
        self.conn = lite.connect(path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()
        self.cur = self.conn.cursor()

    def create_tables(self) -> None:
        self.query(
            "CREATE TABLE IF NOT EXISTS products (idx text, title text, body text, photo blob, price int, tag text)"
        )
        self.query(
            "CREATE TABLE IF NOT EXISTS orders (cid int, usr_name text, usr_address text, products text)"
        )
        self.query(
            "CREATE TABLE IF NOT EXISTS cart (cid int, idx text, quantity int)"
        )
        self.query(
            "CREATE TABLE IF NOT EXISTS categories (idx text, title text)"
        )
        self.query(
            "CREATE TABLE IF NOT EXISTS wallet (cid int, balance real, uid INTEGER UNIQUE PRIMARY KEY NOT NULL)"
        )
        self.query(
            "CREATE TABLE IF NOT EXISTS questions (cid int, question text)"
        )

    def query(self, arg: str, values=None) -> None:
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        self.conn.commit()

    def fetchone(self, arg: str, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchone()

    def fetchall(self, arg: str, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchall()

    def __del__(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass
