# Cấu hình đường dẫn, hằng số
import os

# Đường dẫn file
# Lưu ý: os.path.join giúp code chạy đúng cả trên Windows và Mac/Linux
FILE_MOVIES = os.path.join("data", "movies.csv")
FILE_SHOWTIMES = os.path.join("booking_and_voice_search", "data_structure.json")
FILE_IMAGES = "movie_images.csv"
DB_FILE = "users.db"


# Tài khoản Test
# TEST_USER = "admin"
# TEST_PASS = "123"
# CẤU HÌNH EMAIL
EMAIL_SENDER = "huynhvansi02.02@gmail.com"
EMAIL_PASSWORD = "ajtu lqjj pgkc udsb"

# Hình ảnh
POSTER_PLACEHOLDER = "https://placehold.co/400x600/png?text=No+Poster&font=roboto"
EVENT_BANNERS = [
    "https://www.cgv.vn/media/banner/cache/1/b58515f018eb873dafa430b6f9ae0c1e/9/8/980x448_17__5.jpg",
    "https://iguov8nhvyobj.vcdn.cloud/media/banner/cache/1/b58515f018eb873dafa430b6f9ae0c1e/a/v/avatar3.jpg",
    "https://iguov8nhvyobj.vcdn.cloud/media/banner/cache/1/b58515f018eb873dafa430b6f9ae0c1e/g/h/ghibli.jpg"
]