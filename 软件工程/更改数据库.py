import sqlite3

DB_PATH = "data/word_app.db"

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    # 将中文的“四级”“六级”修改为英文
    cursor.execute("UPDATE words SET level = 'CET4' WHERE level = '四级'")
    cursor.execute("UPDATE words SET level = 'CET6' WHERE level = '六级'")
    conn.commit()

    # 验证修改结果
    cursor.execute("SELECT DISTINCT level FROM words")
    print("当前词书分类有：", cursor.fetchall())