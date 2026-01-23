import os

# 1. Đường dẫn gốc của dự án (D:\Project python)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Định nghĩa thư mục Data
DATA_DIR = os.path.join(BASE_DIR, "data")

# 3. Cấu hình các file trong thư mục data (Tuyệt đối hóa)
FILE_MOVIES = os.path.join(DATA_DIR, "movies.csv")
FILE_RATINGS = os.path.join(DATA_DIR, "ratings.csv")
FILE_IMAGES = os.path.join(DATA_DIR, "movie_images.csv")
DB_FILE = os.path.join(DATA_DIR, "users.db")

# 4. Cấu hình file của module booking (Cập nhật đường dẫn tuyệt đối)
# Giả sử thư mục booking_and_voice_search nằm ở thư mục gốc
FILE_SHOWTIMES = os.path.join(BASE_DIR, "booking_and_voice_search", "data_structure.json")

# --- GIỮ NGUYÊN PHẦN EMAIL VÀ UI ---
EMAIL_SENDER = "huynhvansi02.02@gmail.com"
EMAIL_PASSWORD = "ajtu lqjj pgkc udsb"

POSTER_PLACEHOLDER = "https://placehold.co/400x600/png?text=No+Poster&font=roboto"
EVENT_BANNERS = [
    "https://www.cgv.vn/media/banner/cache/1/b58515f018eb873dafa430b6f9ae0c1e/9/8/980x448_17__5.jpg",
    "https://iguov8nhvyobj.vcdn.cloud/media/banner/cache/1/b58515f018eb873dafa430b6f9ae0c1e/a/v/avatar3.jpg",
    "https://iguov8nhvyobj.vcdn.cloud/media/banner/cache/1/b58515f018eb873dafa430b6f9ae0c1e/g/h/ghibli.jpg"
]