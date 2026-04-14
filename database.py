import sqlite3

DB_PATH = "database.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                is_premium INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

def add_user(user_id: int, username: str):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, username, is_premium) VALUES (?, ?, 0)", (user_id, username))
        conn.commit()

def set_status(user_id: int, status: int):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET is_premium = ? WHERE user_id = ?", (status, user_id))
        conn.commit()

def get_user(user_id: int):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id, is_premium, username FROM users WHERE user_id = ?", (user_id,))
        return c.fetchone()