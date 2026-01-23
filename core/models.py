# Class Movie -
class Movie:
    def __init__(self, id, title, genre, duration, rating, poster, price=45000):
        self.id = id
        self.title = title
        self.genre = genre
        self.duration = duration
        self.rating = rating
        self.poster = poster
        self.price = price

# --- THÊM CLASS USER MỚI ---
class User:
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role  # 0: User, 1: Admin

    def is_admin(self):
        """Hàm tiện ích để kiểm tra nhanh quyền Admin"""
        return self.role == 1