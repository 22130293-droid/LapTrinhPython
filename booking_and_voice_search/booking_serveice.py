import json
import os

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
import uuid

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

    booked_seats = [b["seat"] for b in booked_objects]

    for seat in seats:
        if seat in booked_seats:
            return False

    return True


# 3 Lưu booking
def save_booking(movie_id, date, time, seats):
    data = load_booking_data()
    movie_id = str(movie_id)

    movies = data.setdefault("movies", {})
    movie = movies.setdefault(movie_id, {"showtimes": {}})
    showtimes = movie.setdefault("showtimes", {})
    day = showtimes.setdefault(date, {})
    slot = day.setdefault(time, {"booked_seats": []})

    for seat in seats:
        booking = {
            "booking_id": generate_booking_id(movie_id),
            "seat": seat,
            "price": 105000,
            "status": "BOOKED"
        }
        slot["booked_seats"].append(booking)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return slot["booked_seats"]

