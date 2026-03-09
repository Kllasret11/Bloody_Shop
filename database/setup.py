from __future__ import annotations

from utils.db.storage import DatabaseManager


def setup_db() -> None:
    DatabaseManager().create_tables()
