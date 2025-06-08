import sqlite3
from datetime import datetime

class MistakeManager:
    DB_PATH = "data/word_app.db"  # 数据库路径

    @staticmethod
    def init_table():
        with sqlite3.connect(MistakeManager.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mistakes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    word TEXT,
                    time TEXT,
                    review_count INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

    @staticmethod
    def add_mistake(user_id, word, time=None):
        time = time or datetime.now().strftime('%Y-%m-%d')
        with sqlite3.connect(MistakeManager.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO mistakes (user_id, word, time, review_count)
                VALUES (?, ?, ?, 0)
            ''', (user_id, word, time))
            conn.commit()

    @staticmethod
    def load_mistakes(user_id):
        with sqlite3.connect(MistakeManager.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT word, time, review_count FROM mistakes
                WHERE user_id = ?
            ''', (user_id,))
            rows = cursor.fetchall()

        return [{"word": row[0], "time": row[1], "review_count": row[2]} for row in rows]

    @staticmethod
    def get_review_plan(user_id):
        mistakes = MistakeManager.load_mistakes(user_id)
        plan = []
        for m in mistakes:
            if m["review_count"] < 5:
                plan.append({
                    "word": m["word"],
                    "need_review_times": 5 - m["review_count"]
                })
        return plan

    @staticmethod
    def increment_review_count(user_id, word):
        with sqlite3.connect(MistakeManager.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE mistakes
                SET review_count = review_count + 1
                WHERE user_id = ? AND word = ?
            ''', (user_id, word))
            conn.commit()
