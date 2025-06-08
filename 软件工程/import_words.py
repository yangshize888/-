import sqlite3
import csv
import os

DB_PATH = "data/word_app.db"
WORD_TABLE_NAME = "words"

def init_word_table():
    """初始化单词表"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {WORD_TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                meaning TEXT,
                level TEXT,
                UNIQUE(word, level)  -- 防止重复导入相同单词
            )
        ''')
        conn.commit()

def import_words_from_csv(csv_path):
    """从 CSV 文件导入单词"""
    if not os.path.exists(csv_path):
        print(f"文件不存在：{csv_path}")
        return
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            inserted, skipped = 0, 0
            for row in reader:
                try:
                    cursor.execute(f'''
                        INSERT OR IGNORE INTO {WORD_TABLE_NAME} (word, meaning, level)
                        VALUES (?, ?, ?)
                    ''', (row['word'].strip(), row['meaning'].strip(), row['level'].strip()))
                    inserted += cursor.rowcount
                except Exception as e:
                    print(f"插入失败: {row['word']} - 错误: {e}")
                    skipped += 1
            conn.commit()
        print(f"{csv_path} 导入完成：插入 {inserted} 条，跳过 {skipped} 条")

def batch_import():
    init_word_table()
    import_words_from_csv("cet4.csv")
    import_words_from_csv("cet6.csv")

if __name__ == "__main__":
    batch_import()
