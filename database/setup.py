from database.db import get_connection

def setup_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        reputation INTEGER DEFAULT 0
    )
    """)

    conn.commit()

    cur.close()
    conn.close()