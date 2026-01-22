import sqlite3
import hashlib
import os
from config import DB_FILE

def init_db():
    """Khởi tạo database nếu chưa có"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Tạo bảng users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Mã hóa mật khẩu bằng SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password):
    """Tạo tài khoản mới"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                  (username, email, hash_password(password)))
        conn.commit()
        conn.close()
        return True, "Đăng ký thành công!"
    except sqlite3.IntegrityError:
        return False, "Tên đăng nhập hoặc Email đã tồn tại!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"

def verify_user(username, password):
    """Kiểm tra đăng nhập"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?",
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user # Trả về tuple (id, username, email, pass) hoặc None

def get_user_by_email(email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

def update_password(email, new_password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE email = ?",
              (hash_password(new_password), email))
    conn.commit()
    conn.close()

init_db()