import sqlite3
import hashlib
import os
from config import DB_FILE


def init_db():
    """Khởi tạo database và cập nhật cấu trúc nếu cần"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 1. Tạo bảng users với cột role (0: User, 1: Admin)
    c.execute('''
              CREATE TABLE IF NOT EXISTS users
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  username
                  TEXT
                  UNIQUE
                  NOT
                  NULL,
                  email
                  TEXT
                  UNIQUE
                  NOT
                  NULL,
                  password
                  TEXT
                  NOT
                  NULL,
                  role
                  INTEGER
                  DEFAULT
                  0
              )
              ''')

    # 2. KIỂM TRA VÀ NÂNG CẤP (Dành cho trường hợp file db đã tồn tại từ trước)
    try:
        # Kiểm tra xem cột 'role' đã tồn tại chưa
        c.execute("SELECT role FROM users LIMIT 1")
    except sqlite3.OperationalError:
        # Nếu lỗi nghĩa là chưa có cột role -> Thêm cột vào
        print("🔄 Đang nâng cấp cơ sở dữ liệu: Thêm cột 'role'...")
        c.execute("ALTER TABLE users ADD COLUMN role INTEGER DEFAULT 0")

    conn.commit()
    conn.close()


def hash_password(password):
    """Mã hóa mật khẩu bằng SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username, email, password, role=0):
    """Tạo tài khoản mới (Mặc định là role=0)"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                  (username, email, hash_password(password), role))
        conn.commit()
        conn.close()
        return True, "Đăng ký thành công!"
    except sqlite3.IntegrityError:
        return False, "Tên đăng nhập hoặc Email đã tồn tại!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"


def verify_user(username, password):
    """Kiểm tra đăng nhập - Trả về đầy đủ thông tin bao gồm role"""
    conn = sqlite3.connect(DB_FILE)
    # Cấu hình để kết quả trả về dạng Dictionary cho dễ truy cập tên cột
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?",
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user  # Trả về Row object (có thể truy cập user['role'])


def get_user_by_email(email):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
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


# Hàm bổ trợ để set quyền Admin nhanh (Dùng khi cần tạo tài khoản Admin đầu tiên)
def set_admin_role(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET role = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    print(f"✅ Đã cấp quyền Admin cho tài khoản: {username}")


init_db()