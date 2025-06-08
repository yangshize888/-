import sqlite3

DB_PATH = "data/word_app.db"

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM words")
    total = cursor.fetchone()[0]
    print(f"当前词库中共有 {total} 个单词")

    cursor.execute("SELECT word, level FROM words LIMIT 10")
    for row in cursor.fetchall():
        print(row)
