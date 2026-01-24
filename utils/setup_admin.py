import sys
import os
import sqlite3

# --- ĐOẠN CODE QUAN TRỌNG: Giúp script tìm thấy thư mục gốc dự án ---
# Lấy đường dẫn thư mục gốc (D:\Project python)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Bây giờ có thể import từ core và config bình thường
from core.database import set_admin_role
from config import DB_FILE

# 1. Nhập tên tài khoản đã đăng ký trên giao diện
username_can_cap_quyen = "trqutoan"  # Điền tên đăng ký của vào đây

print(f"--- ĐANG CẤP QUYỀN ADMIN ---")
try:
    # Gọi hàm từ core/database.py
    set_admin_role(username_can_cap_quyen)

    # Kiểm tra lại trực tiếp trong DB_FILE (đường dẫn đã lấy từ config.py)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username = ?", (username_can_cap_quyen,))
    result = c.fetchone()
    conn.close()

    if result and result[0] == 1:
        print(f"✅ THÀNH CÔNG: Tài khoản '{username_can_cap_quyen}' đã là ADMIN.")
    else:
        print(f"❌ THẤT BẠI: Có vẻ tên đăng nhập '{username_can_cap_quyen}' không tồn tại.")

except Exception as e:
    print(f"❌ LỖI HỆ THỐNG: {e}")