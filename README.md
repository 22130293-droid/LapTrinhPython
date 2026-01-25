# 🍿 Cinema AI System - Hệ thống Quản lý & Gợi ý Phim

Dự án cuối khóa môn học Lập trình Python.

## 📂 Cấu trúc thư mục
- `core/`: Xử lý logic nghiệp vụ, kết nối Database và Email service.
- `data/`: Lưu trữ cơ sở dữ liệu SQLite và các file CSV (MovieLens dataset).
- `views/`: Giao diện người dùng xây dựng trên nền tảng Streamlit.
- `modules/`: Các thuật toán AI Recommender và Voice Search.
- `utils/`: Công cụ hỗ trợ khởi tạo hệ thống.

## 🛠 Hướng dẫn cài đặt
Đảm bảo bạn đã cài đặt Python 3.x trên hệ thống.
1. Cài đặt thư viện: `pip install -r requirements.txt`
2. Khởi tạo Admin: `python utils/setup_admin.py`
3. Chạy ứng dụng: `python -m streamlit run main.py`

## ✨ Tính năng chính
- Đăng ký/Đăng nhập & Phân quyền User/Admin.
- Gợi ý phim thông minh (Content-based Filtering). dựa trên từ khóa tìm kiếm hoặc lịch sử mua vé
- Tìm Kiếm với Voice Search.
- Dashboard thống kê dữ liệu dành cho quản trị viên.
- Mua vé dễ dàng với thao tác đặt ghế và qr nhận vé gửi về mail.


