import sqlite3
import hashlib
import os

class UserManager:
    DB_PATH = "data/word_app.db"

    @classmethod
    def init_table(cls):
        os.makedirs("data", exist_ok=True)
        with sqlite3.connect(cls.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL
                )
            ''')
            conn.commit()

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.md5(password.encode('utf-8')).hexdigest()

    @classmethod
    def register_user(cls, username, password, email):
        cls.init_table()
        hashed_pwd = cls.hash_password(password)
        try:
            with sqlite3.connect(cls.DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                    (username, hashed_pwd, email)
                )
                conn.commit()
                return True, cursor.lastrowid
        except sqlite3.IntegrityError as e:
            err = str(e).lower()
            if "username" in err:
                return False, "用户名已存在"
            if "email" in err:
                return False, "邮箱已注册"
            return False, "数据库错误"

    @classmethod
    def login_user(cls, username, password):
        cls.init_table()
        hashed_pwd = cls.hash_password(password)
        with sqlite3.connect(cls.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id FROM users WHERE username = ? AND password = ?',
                (username, hashed_pwd)
            )
            result = cursor.fetchone()
            return result[0] if result else -1
