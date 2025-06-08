import sqlite3
import csv
from user_manager import UserManager

class WordManager:
    DB_PATH = UserManager.DB_PATH

import sqlite3

class WordManager:
    DB_PATH = "data/word_app.db"

    @staticmethod
    def init_word_tables():
        with sqlite3.connect(WordManager.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    meaning TEXT,
                    level TEXT,
                    UNIQUE(word, level)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    word_id INTEGER NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_wrong INTEGER DEFAULT 0,
                    UNIQUE(user_id, word_id),
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(word_id) REFERENCES words(id)
                )
            ''')
            conn.commit()

    @staticmethod
    def import_words_from_csv(csv_path):
        with sqlite3.connect(WordManager.DB_PATH) as conn:
            cursor = conn.cursor()
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    word = row["word"].strip()
                    meaning = row["meaning"].strip()
                    level = row.get("level", "未知").strip()
                    cursor.execute(
                        "INSERT INTO words (word, meaning, level) VALUES (?, ?, ?)",
                        (word, meaning, level)
                    )
            conn.commit()

    @staticmethod
    def add_word_to_user(user_id, word_id):
        with sqlite3.connect(WordManager.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_words (user_id, word_id) VALUES (?, ?)",
                (user_id, word_id)
            )
            conn.commit()

    @staticmethod
    def get_user_word_list(user_id):
        with sqlite3.connect(WordManager.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT w.word, w.meaning, w.level, uw.is_wrong
                FROM user_words uw
                JOIN words w ON uw.word_id = w.id
                WHERE uw.user_id = ?
            ''', (user_id,))
            return cursor.fetchall()

    @staticmethod
    def mark_wrong_word(user_id, word_id):
        with sqlite3.connect(WordManager.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_words
                SET is_wrong = 1
                WHERE user_id = ? AND word_id = ?
            ''', (user_id, word_id))
            conn.commit()
            
    @staticmethod
    def get_next_word(user_id, level):
        with sqlite3.connect(WordManager.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT w.word FROM words w
                LEFT JOIN user_words uw
                ON w.id = uw.word_id AND uw.user_id = ?
                WHERE uw.id IS NULL AND w.level = ?
                LIMIT 1
            ''', (user_id, level))
            row = cursor.fetchone()
            return row[0] if row else "无新单词"

    @staticmethod
    def add_to_favorite(user_id, word):
        with sqlite3.connect(WordManager.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM words WHERE word = ?", (word,))
            word_row = cursor.fetchone()
            if word_row:
                word_id = word_row[0]
                cursor.execute('''
                    INSERT OR IGNORE INTO user_words (user_id, word_id)
                    VALUES (?, ?)
                ''', (user_id, word_id))
                conn.commit()