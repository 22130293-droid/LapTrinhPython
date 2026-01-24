import json
import os
import uuid

DATA_FILE = os.path.join("booking_and_voice_search", "data_structure.json")

# tạo id cho booking
def generate_booking_id(movie_id):
    random_code = uuid.uuid4().hex[:8].upper()  
    return f"SC-{movie_id}-{random_code}"

# 1 Load dữ liệu
def load_booking_data():
    if not os.path.exists(DATA_FILE):
        return {"movies": {}}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 2 Kiểm tra ghế còn trống
def check_availability(movie_id, date, time, seats):
    data = load_booking_data()
    movie_id = str(movie_id)

    booked_objects = (
        data.get("movies", {})
            .get(movie_id, {})
            .get("showtimes", {})
            .get(date, {})
            .get(time, {})
            .get("booked_seats", [])
    )

    booked_seats = [
        b["seat"] if isinstance(b, dict) else b
        for b in booked_objects
    ]

    for seat in seats:
        if seat in booked_seats:
            return False

    return True



# 3 Lưu booking
def save_booking(user_id, movie_id, date, time, seats, price):
    """
    Lưu thông tin đặt vé vào file JSON.
    Hàm đã được nâng cấp để nhận đủ 6 tham số từ giao diện.
    """
    data = load_booking_data()
    movie_id = str(movie_id)

    # Tự động tạo cấu trúc thư mục lồng nhau nếu chưa tồn tại
    movies = data.setdefault("movies", {})
    movie = movies.setdefault(movie_id, {"showtimes": {}})
    showtimes = movie.setdefault("showtimes", {})
    day = showtimes.setdefault(date, {})
    slot = day.setdefault(time, {"booked_seats": []})

    # Duyệt qua danh sách ghế để tạo từng bản ghi booking
    for seat in seats:
        booking = {
            "booking_id": generate_booking_id(movie_id),
            "user_id": user_id,  # Lưu ID người đặt để làm lịch sử
            "seat": seat,
            "price": price / len(seats) if len(seats) > 0 else price, # Chia đều giá cho từng ghế
            "status": "BOOKED",
            "created_at": time # Có thể lưu thêm thời gian tạo nếu muốn
        }
        slot["booked_seats"].append(booking)

    # Ghi dữ liệu mới xuống file JSON
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return slot["booked_seats"]

# hàm lấy thông tin từ json

def get_user_history_json(user_id):
    data = load_booking_data()
    history = []
    movies = data.get("movies", {})

    for m_id, m_data in movies.items():
        showtimes = m_data.get("showtimes", {})
        for s_date, date_data in showtimes.items():
            for s_time, time_data in date_data.items():
                booked_seats = time_data.get("booked_seats", [])
                for ticket in booked_seats:
                    if str(ticket.get("user_id")) == str(user_id):
                        history.append({
                            "booking_id": ticket.get("booking_id"),
                            "movie_id": m_id,
                            "date": s_date,
                            "time": s_time,
                            "seat": ticket.get("seat"),
                            "price": ticket.get("price")
                        })
    return history[::-1]  # Đảo ngược để vé mới nhất lên đầu