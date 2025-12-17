import json
import os

DATA_FILE = os.path.join("backend", "data_structure.json")


# 1 Load dữ liệu
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"movies": {}}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# 2 Kiểm tra ghế còn trống
def check_availability(movie_id, date, time, seats):
    data = load_data()
    movie_id = str(movie_id)

    booked = (
        data.get("movies", {})
            .get(movie_id, {})
            .get("showtimes", {})
            .get(date, {})
            .get(time, {})
            .get("booked_seats", [])
    )

    for seat in seats:
        if seat in booked:
            return False

    return True


# 3 Lưu booking
def save_booking(movie_id, date, time, seats):
    data = load_data()
    movie_id = str(movie_id)

    movies = data.setdefault("movies", {})
    movie = movies.setdefault(movie_id, {"showtimes": {}})
    showtimes = movie.setdefault("showtimes", {})
    day = showtimes.setdefault(date, {})
    slot = day.setdefault(time, {"booked_seats": []})

    slot["booked_seats"].extend(seats)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
