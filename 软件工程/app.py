from flask import Flask, render_template, request, jsonify, session
from user_manager import UserManager  # 导入模块
from mistake_manager import MistakeManager  # 导入模块
from word_manager import WordManager  # 导入模块
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os
from utils.email_utils import send_email
import sqlite3

from 更改数据库 import DB_PATH

app = Flask(__name__)
# 当前书籍状态全局变量（临时方案）
CURRENT_BOOK = {'book': 'CET4'}

@app.route('/')
def index():
    return render_template('index.html')
email_code_map = {}

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/send_code', methods=['POST'])
def send_code():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"success": False, "message": "邮箱不能为空"})

    # 生成6位验证码
    code = ''.join(random.choices(string.digits, k=6))
    email_code_map[email] = code

    # 调用真实发送函数
    success = send_email(email, code)
    if success:
        return jsonify({"success": True, "message": "验证码发送成功"})
    else:
        return jsonify({"success": False, "message": "验证码发送失败，请稍后再试"})

@app.route('/verify_code', methods=['POST'])
def verify_code():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    if not email or not code:
        return jsonify({"success": False, "message": "邮箱和验证码不能为空"})

    real_code = email_code_map.get(email)
    if real_code is None:
        return jsonify({"success": False, "message": "请先发送验证码"})
    if code != real_code:
        return jsonify({"success": False, "message": "验证码错误"})

    # 验证成功后可以允许用户重置密码，这里只示范成功消息
    return jsonify({"success": True, "message": "验证码验证成功"})

@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('new_password')

    if not email or not new_password:
        return jsonify({"success": False, "message": "邮箱和新密码不能为空"})

    # 哈希密码
    hashed = UserManager.hash_password(new_password)

    with sqlite3.connect(UserManager.DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed, email))
        conn.commit()
        if cursor.rowcount > 0:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "邮箱未注册"})
# 登录接口
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "用户名和密码不能为空"}), 400

    user_id = UserManager.login_user(username, password)
    if user_id == -1:
        return jsonify({"success": False, "message": "用户名或密码错误"}), 400
    return jsonify({"success": True, "message": "登录成功", "user_id": user_id})

# 注册页
@app.route('/register')
def register_page():
    return render_template('register.html')

# 注册接口
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({"success": False, "message": "用户名、密码和邮箱不能为空"}), 400

    success, result = UserManager.register_user(username, password, email)
    if success:
        return jsonify({"success": True, "message": "注册成功", "user_id": result})
    else:
        return jsonify({"success": False, "message": result}), 400


@app.route('/dashboard')
def dashboard():
    user_id = request.args.get("user_id")
    if not user_id:
        return "用户ID缺失", 400
    try:
        user_id_int = int(user_id)
    except ValueError:
        return "用户ID格式错误", 400
    # 这里可以做更多权限或用户有效性校验
    return render_template("dashboard.html", user_id=user_id_int)


@app.route('/api/next_word')
def get_next_word():
    user_id = request.args.get("user_id", type=int)
    level = session.get("book", "CET4")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT w.id, w.word, w.meaning FROM words w
            WHERE w.level = ?
              AND w.id NOT IN (
                  SELECT uw.word_id FROM user_words uw WHERE uw.user_id = ?
              )
            ORDER BY RANDOM()
            LIMIT 1
        ''', (level, user_id))

        row = cursor.fetchone()
        if row:
            word_id, word, meaning = row
            # 保存到 user_words 中（表示已展示）
            cursor.execute('''
                INSERT INTO user_words (user_id, word_id)
                VALUES (?, ?)
            ''', (user_id, word_id))
            conn.commit()
            return jsonify({"status": "ok", "word": word, "meaning": meaning})
        else:
            return jsonify({"status": "done", "word": "", "meaning": ""})



@app.route("/api/favorite", methods=["POST"])
def add_to_favorite():
    data = request.get_json()
    WordManager.add_to_favorite(data["user_id"], data["word"])
    return jsonify({"status": "success"})

@app.route("/api/mistake", methods=["POST"])
def mark_as_mistake():
    data = request.get_json()
    MistakeManager.mark_mistake(data["user_id"], data["word"])
    return jsonify({"status": "success"})

@app.route("/api/set_book", methods=["POST"])
def set_book():
    data = request.get_json()
    CURRENT_BOOK['book'] = data.get("book", "CET4")
    return jsonify({"status": "book switched", "book": CURRENT_BOOK['book']})


@app.route('/api/remember', methods=['POST'])
def mark_remembered():
    data = request.get_json()
    user_id = data.get("user_id")
    word = data.get("word")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM words WHERE word = ?', (word,))
        row = cursor.fetchone()
        if row:
            word_id = row[0]
            # 更新为不是错误单词
            cursor.execute('''
                UPDATE user_words
                SET is_wrong = 0
                WHERE user_id = ? AND word_id = ?
            ''', (user_id, word_id))
            conn.commit()
            return jsonify({"status": "ok"})
        return jsonify({"status": "error", "msg": "word not found"})




if __name__ == '__main__':
    MistakeManager.init_table()  # 初始化数据库表
    UserManager.init_table()  # 初始化数据库表
    WordManager.init_word_tables()  # 初始化数据库表
    app.run(debug=True)