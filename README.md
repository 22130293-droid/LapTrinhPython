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
- Gợi ý phim thông minh (Content-based Filtering).
- Đặt vé trực tuyến với Voice Search.
- Dashboard thống kê dữ liệu dành cho quản trị viên.

Phân công:
Thành viên 1
AI Data Specialist
- Tiền xử lý dữ liệu MovieLens (Clean data).
- Xây dựng thuật toán Recommender System (Content-based).
- Viết hàm tìm kiếm phim theo từ khóa/thể loại.
- Tích hợp module gợi ý phim vào ứng dụng (app.py)
Thành viên 2
Backend & Voice Engineer
- Tích hợp Whisper AI để xử lý âm thanh.
- Thiết kế cấu trúc file JSON.
- Viết các hàm logic Backend: load_data(), save_booking(), check_availability().
Thành viên 3
Frontend Developer 
- Xây dựng giao diện Web bằng Streamlit.(
   + Tạo môi trường ảo mới: python -m venv venv
   + Kích hoạt môi trường: .\venv\Scripts\activate
   + Run: streamlit run app.py
)
- Cài đặt thư viện SpeechRecognition.(
   + pip install SpeechRecognition
)
- Cài đặt thư viện streamlit-extras. (
  + pip install streamlit-extras
)
- Thiết kế UI sơ đồ ghế ngồi (Grid layout).
- Tích hợp code của TV2 vào ứng dụng chính (app.py).
- Tìm kiếm hình ảnh/poster phim để làm đẹp giao diện.

