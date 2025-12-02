Movie_pyProject/
├── .git/
├── **README.md** # Mô tả dự án, hướng dẫn chạy, phân công. Danh sách thư viện cần thiết .
├── **app.py** # (Thành viên 3 - Frontend) File ứng dụng Streamlit chính.
├── **ai_module/** # (Thành viên 1 - AI Data Specialist)
│   ├── **__init__.py**
│   ├── **recommender.py** # Code thuật toán gợi ý 
│   └── **data_processor.py** # Hàm tiền xử lý dữ liệu (Clean data)
|
├── **backend_module/** # (Thành viên 2 - Backend & Voice Engineer)
│   ├── **__init__.py**
│   ├── **voice_handler.py** # Tích hợp Whisper AI để xử lý âm thanh (Voice Engineer)
│   ├── **logic.py** # Chứa các hàm logic backend: load_data(), save_booking(), check_availability().
│   └── **data_structure.json** # File JSON mẫu (Cấu trúc file JSON)
|
├── **data/** # Nơi lưu trữ dữ liệu nguồn
│   ├── **movies.csv** # Dataset nguồn
│   ├── **cleaned_data.csv** # Lưu trữ dữ liệu sau khi tiền xử lý
│   └── **posters/** # (Thành viên 3) Thư mục chứa hình ảnh/poster phim (nếu không dùng API)
|
└── **docs/** 
    └── **task_assignment.md** #  File chi tiết phân công công việc & tiến độ.
_____________________________________________________
Thành viên 1
AI Data Specialist
- Tiền xử lý dữ liệu MovieLens (Clean data).
- Xây dựng thuật toán Recommender System (Content-based).
- Viết hàm tìm kiếm phim theo từ khóa/thể loại.
Thành viên 2
Backend & Voice Engineer
- Tích hợp Whisper AI để xử lý âm thanh.
- Thiết kế cấu trúc file JSON.
- Viết các hàm logic Backend: load_data(), save_booking(), check_availability().
Thành viên 3
Frontend Developer 
- Xây dựng giao diện Web bằng Streamlit.
- Thiết kế UI sơ đồ ghế ngồi (Grid layout).
- Tích hợp code của TV1 và TV2 vào ứng dụng chính (app.py).
- Tìm kiếm hình ảnh/poster phim để làm đẹp giao diện.

