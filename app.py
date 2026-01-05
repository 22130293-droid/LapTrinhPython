import streamlit as st
import time as et
import pandas as pd
import os
import random

# --- BỔ SUNG IMPORTS TỪ MODULE AI CỦA THÀNH VIÊN 1 ---
from movie_recommender_ai_module.data_processor import load_data
from movie_recommender_ai_module.recommender import ContentBasedRecommender

# --- BOOKING VÀ MODULE AI VOICE SEARCH THÀNH VIÊN 2 ---
from booking_and_voice_search.booking_serveice import check_availability, load_booking_data, save_booking
from booking_and_voice_search.voice_controller import VoiceSearchController

# --- 1. CẤU HÌNH & HẰNG SỐ ---
st.set_page_config(page_title="Cinema AI System", page_icon="🍿", layout="wide")

# Đường dẫn file
FILE_MOVIES = os.path.join("data", "movies.csv")
FILE_SHOWTIMES = os.path.join("booking_and_voice_search", "data_structure.json")
FILE_IMAGES = "movie_images.csv"

# --- TÀI KHOẢN TEST (Login) ---
TEST_USER = "admin"
TEST_PASS = "123"

# Ảnh mặc định
POSTER_PLACEHOLDER = "https://placehold.co/400x600/png?text=No+Poster&font=roboto"

# Danh sách ảnh Banner
EVENT_BANNERS = [
    "https://www.cgv.vn/media/banner/cache/1/b58515f018eb873dafa430b6f9ae0c1e/9/8/980x448_17__5.jpg",
    "https://iguov8nhvyobj.vcdn.cloud/media/banner/cache/1/b58515f018eb873dafa430b6f9ae0c1e/a/v/avatar3.jpg",
    "https://iguov8nhvyobj.vcdn.cloud/media/banner/cache/1/b58515f018eb873dafa430b6f9ae0c1e/g/h/ghibli.jpg"
]

# --- 2. HÀM TẠO DỮ LIỆU ẢNH MẪU ---
def create_demo_image_file():
    """Tự động tạo file movie_images.csv chứa link ảnh thật."""
    if not os.path.exists(FILE_IMAGES):
        csv_content = """movieId,poster_url
1,https://image.tmdb.org/t/p/w500/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg
2,https://image.tmdb.org/t/p/w500/kzC6J8D10x9XoT6Y1q5Q8h5v5a.jpg
3,https://image.tmdb.org/t/p/w500/1FSXpj5e8l4KH6nVFO5SPUeraOt.jpg
4,https://image.tmdb.org/t/p/w500/3s9O5af2xWKWR5JzP2iJZpZeQQg.jpg
5,https://image.tmdb.org/t/p/w500/rj4LBtwQ0uGrhKneQXMNCNLHqnB.jpg
6,https://image.tmdb.org/t/p/w500/rrBuGu0PjqhYYLOBS1qvU6NNPCk.jpg
7,https://image.tmdb.org/t/p/w500/hN12586259n64c0X1Xj0X9Xz9X.jpg
8,https://image.tmdb.org/t/p/w500/z4x0Bp48ar3Mda8KiPD1n652Wq.jpg
9,https://image.tmdb.org/t/p/w500/2jfloY2aJ2k2Z2j2.jpg
10,https://image.tmdb.org/t/p/w500/5c0ovQPME0.jpg
11,https://image.tmdb.org/t/p/w500/yFihWxQcmqcaXdaDpxxjC.jpg
12,https://image.tmdb.org/t/p/w500/4rC8n6XZ.jpg
13,https://image.tmdb.org/t/p/w500/gV9v6M.jpg
14,https://image.tmdb.org/t/p/w500/c5454.jpg
15,https://image.tmdb.org/t/p/w500/x555.jpg
16,https://image.tmdb.org/t/p/w500/4T.jpg
17,https://image.tmdb.org/t/p/w500/1.jpg
18,https://image.tmdb.org/t/p/w500/2.jpg
19,https://image.tmdb.org/t/p/w500/3.jpg
20,https://image.tmdb.org/t/p/w500/4.jpg
21,https://image.tmdb.org/t/p/w500/yFihWxQcmqcaXdaDpxxjC.jpg
25,https://image.tmdb.org/t/p/w500/yFihWxQcmqcaXdaDpxxjC.jpg
32,https://image.tmdb.org/t/p/w500/aBw8zYuAljVM1qvKqlFcaMwYm0Z.jpg
34,https://image.tmdb.org/t/p/w500/b9gTJKLdSbwcQRKftjdV9tr8lHu.jpg
39,https://image.tmdb.org/t/p/w500/yFihWxQcmqcaXdaDpxxjC.jpg
47,https://image.tmdb.org/t/p/w500/6yoghtyTpznpBik8EngEmJskVUO.jpg
48,https://image.tmdb.org/t/p/w500/2lECpi35Hnbpa4y46JX0aY3AWTy.jpg
50,https://image.tmdb.org/t/p/w500/bUP17S2176nJ3R624s9f9k0p.jpg
110,https://image.tmdb.org/t/p/w500/or1gBugydmjToiUqIMRwMN56LXR.jpg
150,https://image.tmdb.org/t/p/w500/811DjJTon9gD6hZ8nCjSitaIXFQ.jpg
153,https://image.tmdb.org/t/p/w500/hN12586259n64c0X1Xj0X9Xz9X.jpg
161,https://image.tmdb.org/t/p/w500/hN12586259n64c0X1Xj0X9Xz9X.jpg
165,https://image.tmdb.org/t/p/w500/hN12586259n64c0X1Xj0X9Xz9X.jpg
260,https://image.tmdb.org/t/p/w500/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg
293,https://image.tmdb.org/t/p/w500/fR2v2sN5m1G2tXF9rF8a5r5.jpg
296,https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg
316,https://image.tmdb.org/t/p/w500/hN12586259n64c0X1Xj0X9Xz9X.jpg
318,https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg
344,https://image.tmdb.org/t/p/w500/yFihWxQcmqcaXdaDpxxjC.jpg
356,https://image.tmdb.org/t/p/w500/saHP97rTPS5eLmrLQEcANmKrsFl.jpg
364,https://image.tmdb.org/t/p/w500/sKCr78MXSLixwmZ8DyJLrpMsd15.jpg
367,https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6babgKnONONX.jpg
377,https://image.tmdb.org/t/p/w500/u3bZgnGQ9TWASq28QCRuXFIAl2f.jpg
457,https://image.tmdb.org/t/p/w500/hN12586259n64c0X1Xj0X9Xz9X.jpg
480,https://image.tmdb.org/t/p/w500/oU7Oq2kFAAlGqbU4VoNCQaHTbdk.jpg
527,https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pTXMYnljO.jpg
541,https://image.tmdb.org/t/p/w500/3W0v956XxSG5xgm7LB6qu8ExYJ2.jpg
588,https://image.tmdb.org/t/p/w500/3s5mr6t2iZfW2N2Q9j4f4.jpg
589,https://image.tmdb.org/t/p/w500/vlxJHkBfC3QfS5k490.jpg
593,https://image.tmdb.org/t/p/w500/rplLJ2hPcOQmkFhTqUte0MkEaO2.jpg
608,https://image.tmdb.org/t/p/w500/w7RDIgQM6bLT7JXtH4i4.jpg
780,https://image.tmdb.org/t/p/w500/jS15a.jpg
858,https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg
1097,https://image.tmdb.org/t/p/w500/prMUg4.jpg
1196,https://image.tmdb.org/t/p/w500/7BuH8itoDDemLo6YNEqUM8496l9.jpg
1197,https://image.tmdb.org/t/p/w500/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg
1198,https://image.tmdb.org/t/p/w500/ceG9VzoRAVGwivFU403Wc3AHRys.jpg
1210,https://image.tmdb.org/t/p/w500/5UU3bY.jpg
1214,https://image.tmdb.org/t/p/w500/2TeJfUz3wolxUyLSAVjoPHpROJ.jpg
1240,https://image.tmdb.org/t/p/w500/eI28.jpg
1265,https://image.tmdb.org/t/p/w500/sl7F.jpg
1270,https://image.tmdb.org/t/p/w500/oZkT.jpg
1291,https://image.tmdb.org/t/p/w500/39d.jpg
1580,https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg
1704,https://image.tmdb.org/t/p/w500/6WBeq4fCfn7AN0o21W9qNcRF2l9.jpg
1721,https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg
2028,https://image.tmdb.org/t/p/w500/w2PMyoyLU22YvrGKQspY2j5RPp7.jpg
2329,https://image.tmdb.org/t/p/w500/xCIHBc3n11jG66e.jpg
2571,https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg
2762,https://image.tmdb.org/t/p/w500/4q2NNj4S5dG2RLF9CpXsej7yXl.jpg
2858,https://image.tmdb.org/t/p/w500/h5J4W4ive189AmN.jpg
2959,https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg
3578,https://image.tmdb.org/t/p/w500/uS15Au.jpg
3996,https://image.tmdb.org/t/p/w500/kiwO58MM.jpg
4226,https://image.tmdb.org/t/p/w500/khsj.jpg
4306,https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg
4886,https://image.tmdb.org/t/p/w500/eKi8dIr8mpCdD67.jpg
4993,https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg
5816,https://image.tmdb.org/t/p/w500/qjAH13.jpg
5952,https://image.tmdb.org/t/p/w500/5VTN0nR8Enthghbp5ECAu8.jpg
6377,https://image.tmdb.org/t/p/w500/eN1T.jpg
6539,https://image.tmdb.org/t/p/w500/t.jpg
6874,https://image.tmdb.org/t/p/w500/6u.jpg
7153,https://image.tmdb.org/t/p/w500/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg
7361,https://image.tmdb.org/t/p/w500/kOVEVeg59E0ws.jpg
8961,https://image.tmdb.org/t/p/w500/2.jpg
33794,https://image.tmdb.org/t/p/w500/w.jpg
44191,https://image.tmdb.org/t/p/w500/w7.jpg
48780,https://image.tmdb.org/t/p/w500/ycTypeZ9.jpg
58559,https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg
59315,https://image.tmdb.org/t/p/w500/78lPtwv72eTNqFW9COBYI0dWDJa.jpg
60069,https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWXpVr.jpg
68157,https://image.tmdb.org/t/p/w500/hE24GYddaxB9MVZl1C6tW.jpg
68954,https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg
72998,https://image.tmdb.org/t/p/w500/kyeqWdyUXW608qlYkRqosgbbJyK.jpg
79132,https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg
79702,https://image.tmdb.org/t/p/w500/w9kR8qbmQ01HwnvK4alvnQ2ca0L.jpg
89745,https://image.tmdb.org/t/p/w500/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg
91500,https://image.tmdb.org/t/p/w500/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg
91529,https://image.tmdb.org/t/p/w500/811DjJTon9gD6hZ8nCjSitaIXFQ.jpg
99114,https://image.tmdb.org/t/p/w500/4ss4052TqAV0oF4ue7xP7Q0Ev0h.jpg
109374,https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg
109487,https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg
112552,https://image.tmdb.org/t/p/w500/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg
112852,https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg
115617,https://image.tmdb.org/t/p/w500/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg
116797,https://image.tmdb.org/t/p/w500/3jcNjAUVNV94BT9Q3tVf5hX6g8I.jpg
122882,https://image.tmdb.org/t/p/w500/69Szs9l341Q0B33923q4852.jpg
122904,https://image.tmdb.org/t/p/w500/5Tsw7bJ9n9n5M5q2t7r4.jpg
122920,https://image.tmdb.org/t/p/w500/m1.jpg
134130,https://image.tmdb.org/t/p/w500/db32LaOibwEliAmSL2jjDF6oDdj.jpg
134853,https://image.tmdb.org/t/p/w500/jjBgi2r5cRt36xF6iNUEhzscEcb.jpg
139385,https://image.tmdb.org/t/p/w500/hE24GYddaxB9MVZl1C6tW.jpg
148626,https://image.tmdb.org/t/p/w500/xT98tLpV01RwgpldB9Z1t6.jpg
152081,https://image.tmdb.org/t/p/w500/czM5.jpg
164179,https://image.tmdb.org/t/p/w500/qjAH13.jpg
166528,https://image.tmdb.org/t/p/w500/yEs2.jpg
168252,https://image.tmdb.org/t/p/w500/tWqIfL5.jpg
174055,https://image.tmdb.org/t/p/w500/6Jj.jpg
176371,https://image.tmdb.org/t/p/w500/c9XxwwhPHdaImA2f1WEfEsbhaFB.jpg
177593,https://image.tmdb.org/t/p/w500/mY7SeH4HFFxW1hiI6cWuwCRKptN.jpg
177765,https://image.tmdb.org/t/p/w500/kOVEVeg59E0ws.jpg
179401,https://image.tmdb.org/t/p/w500/c9XxwwhPHdaImA2f1WEfEsbhaFB.jpg
179819,https://image.tmdb.org/t/p/w500/5.jpg
180031,https://image.tmdb.org/t/p/w500/8dTWj3c74bWw2p.jpg
183897,https://image.tmdb.org/t/p/w500/kOVEVeg59E0ws.jpg
187593,https://image.tmdb.org/t/p/w500/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg
187595,https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6babgKnONONX.jpg
"""
        with open(FILE_IMAGES, "w") as f:
            f.write(csv_content)

# --- 3. LỚP ĐỐI TƯỢNG (MODEL) ---
class Movie:
    def __init__(self, id, title, genre, duration, rating, poster, price):
        self.id = id
        self.title = title
        self.genre = genre
        self.duration = duration
        self.rating = rating
        self.poster = poster
        self.price = price

# --- 4. XỬ LÝ DỮ LIỆU & CACHE ---
@st.cache_resource
def get_cached_data():
    """
    Tải dữ liệu 1 lần duy nhất để:
    1. Cố định danh sách phim hiển thị (tránh random giá/giờ lại mỗi khi render).
    2. Load Full Dataset để phục vụ tìm kiếm.
    """
    create_demo_image_file()
    df_movies = load_data() # Dữ liệu gốc (9000+ phim)
    recommender = None
    movies_list_ui = [] # Danh sách rút gọn 50 phim cho UI Carousel

    if not df_movies.empty:
        # Merge dữ liệu ảnh
        if os.path.exists(FILE_IMAGES):
            try:
                df_imgs = pd.read_csv(FILE_IMAGES)
                df_movies['movieId'] = df_movies['movieId'].astype(int)
                df_imgs['movieId'] = df_imgs['movieId'].astype(int)
                df_movies = pd.merge(df_movies, df_imgs[['movieId', 'poster_url']], on='movieId', how='left')
            except Exception:
                df_movies['poster_url'] = None
        else:
            df_movies['poster_url'] = None

        # Train Model
        recommender = ContentBasedRecommender(df_movies)

        # Tạo danh sách Movie cho Carousel (Top 50)
        # Fix cứng thông tin ở đây để không bị nhảy khi rerender
        for index, row in df_movies.head(50).iterrows():
            movies_list_ui.append(_create_movie_from_row(row))
            
    if not movies_list_ui:
        movies_list_ui = [Movie(1, "Phim Demo", "Hành động", "120p", "C18", POSTER_PLACEHOLDER, 100000)]

    return recommender, movies_list_ui, df_movies

def _create_movie_from_row(row):
    """Helper function để tạo Movie object từ 1 dòng dataframe."""
    img_link = POSTER_PLACEHOLDER
    if 'poster_url' in row and pd.notna(row['poster_url']) and str(row['poster_url']).strip() != "":
        img_link = row['poster_url']
    else:
        safe_title = str(row['title']).split('(')[0].strip().replace(' ', '+')
        img_link = f"https://placehold.co/400x600?text={safe_title}"

    # Tạo giá và thời lượng giả lập (Dựa trên ID để cố định, không dùng random thuần túy)
    random.seed(int(row['movieId'])) 
    price = random.choice([90000, 105000, 120000, 150000])
    duration = f"{random.randint(90, 160)}'"
    
    return Movie(
        id=row['movieId'],
        title=row['title'],
        genre=str(row['genres']).replace('|', ', '),
        duration=duration,
        rating=f"⭐ {row['average_rating']:.1f}",
        poster=img_link,
        price=price
    )

# --- 5. LỚP DỊCH VỤ (SERVICE) ---
class CinemaService:
    def __init__(self):
        self.showtimes = {}
        self.booked_seats_db = {}
        # Lấy dữ liệu từ Cache: recommender, list hiển thị, và FULL DATA
        self.recommender, self.movies, self.full_df = get_cached_data()
        self.load_or_build_virtual_backend()

    def load_or_build_virtual_backend(self):
        self.showtimes = {
            "Hôm nay": ["09:30", "11:00", "14:15", "19:00", "21:30", "23:00"],
            "Ngày mai": ["10:00", "13:00", "18:00", "20:00"],
            "Ngày kia": ["09:00", "15:00", "19:30"]
        }
        self.booked_seats_db = {}
        if self.movies:
            key = f"{self.movies[0].id}_Hôm nay_19:00"
            self.booked_seats_db[key] = ["A3", "A4", "A5", "C4", "C5"]

    def get_all_movies(self):
        return self.movies

    def get_movie_by_id(self, id):
        # 1. Tìm trong list 50 phim hiển thị trước
        for m in self.movies:
            if m.id == id: return m
        
        # 2. Nếu không thấy (do search ra phim cũ), tìm trong Full Dataset
        if not self.full_df.empty:
            row = self.full_df[self.full_df['movieId'] == id]
            if not row.empty:
                return _create_movie_from_row(row.iloc[0])
        
        return None

    def get_seat_layout(self, m_id, d, t):
        data = load_booking_data()
        m_id = str(m_id)
        booked = data.get("movies", {}).get(m_id, {}).get("showtimes", {}).get(d, {}).get(t, {}).get("booked_seats", [])
        return [
            [1 if f"{chr(65 + r)}{c + 1}" in booked else 0 for c in range(8)]
            for r in range(6)
        ]

    def get_recommendations(self, title):
        if self.recommender:
            return self.recommender.get_recommendations(title)
        return []

# --- 6. LỚP GIAO DIỆN (UI) ---
class CinemaAppUI:
    def __init__(self):
        self.service = CinemaService()
        self.voice_controller = VoiceSearchController()
        self.inject_custom_css()

        # State Management
        if 'page' not in st.session_state: st.session_state['page'] = 'home'
        if "voice_query" not in st.session_state: st.session_state["voice_query"] = ""
        if "fill_from_voice" not in st.session_state: st.session_state["fill_from_voice"] = False
        if 'movie_index' not in st.session_state: st.session_state['movie_index'] = 0
        if 'selected_movie_id' not in st.session_state: st.session_state['selected_movie_id'] = None
        if 'selected_seats' not in st.session_state: st.session_state['selected_seats'] = []
        if 'selected_date' not in st.session_state: st.session_state['selected_date'] = "Hôm nay"
        if 'selected_time' not in st.session_state: st.session_state['selected_time'] = "19:00"
        
        # Login State
        if 'is_logged_in' not in st.session_state: st.session_state['is_logged_in'] = False
        if 'username' not in st.session_state: st.session_state['username'] = ""
        if 'pre_login_page' not in st.session_state: st.session_state['pre_login_page'] = 'home'

    def inject_custom_css(self):
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&family=Roboto:wght@300;400;700&display=swap');
            
            /* --- GLOBAL THEME --- */
            .stApp { 
                background: radial-gradient(circle at top, #1b1b2f 0%, #16213e 50%, #0f3460 100%); 
                color: #FFFFFF; 
                font-family: 'Montserrat', sans-serif; 
            }
            
            h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; text-shadow: 0 4px 6px rgba(0,0,0,0.3); font-weight: 800 !important; }
            p, span, div, label { color: #e0e0e0; }

            /* --- CUSTOM BUTTONS --- */
            div.stButton > button {
                background: linear-gradient(90deg, #e52d27 0%, #b31217 100%);
                color: white !important;
                border: none;
                border-radius: 25px;
                padding: 10px 24px;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(229, 45, 39, 0.4);
            }
            div.stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(229, 45, 39, 0.6);
            }
            /* Nút phụ (Secondary) */
            div.stButton > button[kind="secondary"] {
                background: transparent;
                border: 1px solid rgba(255,255,255,0.3);
                box-shadow: none;
            }

            /* --- HEADER GLASSMORPHISM --- */
            .header-container {
                display: flex; justify-content: space-between; align-items: center;
                padding: 15px 30px;
                background: rgba(255, 255, 255, 0.03);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 0 0 20px 20px;
                margin-bottom: 30px;
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            }
            .logo { 
                font-size: 32px; font-weight: 900; letter-spacing: 2px;
                background: linear-gradient(to right, #ff416c, #ff4b2b); 
                -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                text-decoration: none !important; 
            }

            /* --- BANNER SLIDER (TỈ LỆ 21:9 - CINEMATIC) --- */
            .slider-frame { 
                overflow: hidden; 
                width: 100%; 
                aspect-ratio: 21/9; /* Tỉ lệ chuẩn điện ảnh */
                max-height: 550px;
                margin-bottom: 50px; 
                border-radius: 20px; 
                position: relative; 
                box-shadow: 0 20px 50px rgba(0,0,0,0.5); 
                border: 1px solid rgba(255,255,255,0.1); 
            }
            .slide-images { 
                width: 300%; height: 100%; display: flex; 
                animation: slide_animation 18s infinite cubic-bezier(0.45, 0, 0.55, 1); 
            }
            .img-container { width: 100%; height: 100%; position: relative; }
            .img-container img { 
                width: 100%; height: 100%; 
                object-fit: cover; /* Đảm bảo ảnh lấp đầy khung tỉ lệ 21:9 */
                object-position: center 20%; 
            }
            
            @keyframes slide_animation { 
                0%, 28% { margin-left: 0%; } 
                33%, 61% { margin-left: -100%; } 
                66%, 94% { margin-left: -200%; } 
                100% { margin-left: 0%; } 
            }

            /* --- MOVIE CARD UPGRADE --- */
            .movie-container { 
                background: rgba(255, 255, 255, 0.05); 
                backdrop-filter: blur(5px);
                border-radius: 16px; padding: 12px; 
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
                border: 1px solid rgba(255, 255, 255, 0.05); 
                height: 100%; 
                position: relative;
                overflow: hidden;
            }
            .movie-container:hover { 
                transform: translateY(-10px) scale(1.02); 
                border-color: #ff4b2b; 
                box-shadow: 0 15px 30px rgba(255, 75, 43, 0.2); 
                background: rgba(255, 255, 255, 0.1);
            }
            .movie-img-box { 
                border-radius: 12px; overflow: hidden; margin-bottom: 12px; 
                aspect-ratio: 2/3; /* Tỉ lệ Poster Chuẩn */
                position: relative; 
            }
            .movie-img-box img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; }
            .movie-container:hover .movie-img-box img { transform: scale(1.1); }
            
            .movie-title { font-family: 'Montserrat', sans-serif; font-size: 16px; font-weight: 700; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #FFF; }
            .tag { background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 6px; font-size: 11px; color: #bbb; border: 1px solid rgba(255,255,255,0.1); }

            /* --- BOOKING SEATS --- */
            div[data-testid="column"] button {
                padding: 0px !important;
                min-height: 40px !important;
                border-radius: 8px 8px 15px 15px !important; /* Hình dáng ghế ngồi */
                margin: 2px !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
            }
            
            /* --- FOOTER --- */
            .footer {
                margin-top: 80px;
                padding: 40px 20px;
                background: rgba(0,0,0,0.3);
                border-top: 1px solid rgba(255,255,255,0.1);
                text-align: center;
                font-size: 14px;
                color: #888;
            }
            .footer a { color: #ff4b2b; text-decoration: none; font-weight: bold; margin: 0 10px; transition: 0.3s; }
            .footer a:hover { color: #fff; text-shadow: 0 0 10px #ff4b2b; }
            .footer-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; max-width: 1000px; margin: 0 auto 30px auto; text-align: left; }
            .footer-col h4 { color: #fff; margin-bottom: 15px; font-size: 16px; text-transform: uppercase; letter-spacing: 1px; }

            /* --- INPUT FIELDS --- */
            div[data-testid="stTextInput"] input {
                background-color: rgba(255,255,255,0.1);
                color: white;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.1);
            }
            div[data-testid="stTextInput"] input:focus {
                border-color: #ff4b2b;
                box-shadow: 0 0 10px rgba(255, 75, 43, 0.3);
            }
            </style>
        """, unsafe_allow_html=True)

    def render_header(self):
        with st.container():
            st.markdown('<div class="header-container">', unsafe_allow_html=True)
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1.5])
            
            with c1: st.markdown('<a href="#" class="logo">🍿 START CINEMA</a>', unsafe_allow_html=True)
            
            with c2: 
                if st.button("TRANG CHỦ", key="nav_home"): 
                    st.session_state['page'] = 'home'
                    st.rerun()
            with c3: st.button("LỊCH CHIẾU", key="nav_event")
            
            with c4:
                if st.button("THÀNH VIÊN", key="nav_member"):
                    if st.session_state['is_logged_in']:
                        st.toast(f"Xin chào: {st.session_state['username']}")
                    else:
                        st.session_state['pre_login_page'] = 'home'
                        st.session_state['page'] = 'login'
                        st.rerun()

            with c5:
                if st.session_state['is_logged_in']:
                    if st.button(f"Logout ({st.session_state['username']})", key="logout_btn"):
                         st.session_state['is_logged_in'] = False
                         st.session_state['username'] = ""
                         st.rerun()
                else:
                    if st.button("🔐 ĐĂNG NHẬP", key="login_btn_header"):
                        st.session_state['pre_login_page'] = 'home'
                        st.session_state['page'] = 'login'
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    def render_footer(self):
        st.markdown("""
            <div class="footer">
                <div class="footer-grid">
                    <div class="footer-col">
                        <h4>Về Start Cinema</h4>
                        <p>Hệ thống rạp chiếu phim hiện đại hàng đầu với công nghệ AI gợi ý phim thông minh và trải nghiệm đặt vé mượt mà.</p>
                    </div>
                    <div class="footer-col">
                        <h4>Liên kết nhanh</h4>
                        <p><a href="#">Tuyển dụng</a></p>
                        <p><a href="#">Điều khoản sử dụng</a></p>
                        <p><a href="#">Chính sách bảo mật</a></p>
                    </div>
                    <div class="footer-col">
                        <h4>Liên hệ</h4>
                        <p>📍 Dĩ An, Bình Dương, Vietnam</p>
                        <p>📞 1900 1234</p>
                        <p>📧 support@startcinema.vn</p>
                    </div>
                </div>
                <hr style="border-color: rgba(255,255,255,0.1); margin-bottom: 20px;">
                <p>&copy; 2026 START CINEMA AI SYSTEM. All rights reserved.</p>
                <div>
                    <a href="#">Facebook</a> • <a href="#">Instagram</a> • <a href="#">Youtube</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    def render_login(self):
        self.render_header()
        st.markdown("<br><br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.markdown("""
                <div style="text-align: center; margin-bottom: 20px;">
                    <h2 style="background: linear-gradient(to right, #ff416c, #ff4b2b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">WELCOME BACK</h2>
                    <p>Vui lòng đăng nhập để tiếp tục</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("Tên đăng nhập", placeholder="admin")
                password = st.text_input("Mật khẩu", type="password", placeholder="123")
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("ĐĂNG NHẬP NGAY", type="primary", use_container_width=True)
                
                if submitted:
                    if username == TEST_USER and password == TEST_PASS:
                        st.session_state['is_logged_in'] = True
                        st.session_state['username'] = username
                        st.success("Đăng nhập thành công!")
                        et.sleep(0.5)
                        st.session_state['page'] = st.session_state['pre_login_page']
                        st.rerun()
                    else:
                        st.error("Sai tài khoản hoặc mật khẩu!")

    def render_home(self):
        self.render_header()
        
        # SLIDER HTML
        imgs_html = "".join([f'<div class="img-container"><img src="{url}"></div>' for url in EVENT_BANNERS])
        st.markdown(f"""
            <div class="slider-frame">
                <div class="slide-images">{imgs_html}</div>
                <div style="position: absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(180deg, rgba(27,27,47,0.2) 0%, rgba(27,27,47,0) 50%, rgba(15,52,96,0.6) 100%); pointer-events: none;"></div>
            </div>
        """, unsafe_allow_html=True)

        listening_placeholder = st.empty()
        if st.session_state.get("fill_from_voice"):
            st.session_state["manual_search_input"] = st.session_state["voice_query"]
            st.session_state["fill_from_voice"] = False

        st.markdown("<h3 style='margin-bottom: 20px; border-left: 5px solid #ff4b2b; padding-left: 15px; text-transform: uppercase; letter-spacing: 1px;'>🔥 Phim Đang Chiếu</h3>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([3, 1.5])
        with c2:
            col_in, col_btn = st.columns([5, 1])
            search_query = col_in.text_input("Search", placeholder="🔍 Tìm tên phim...", key="manual_search_input", label_visibility="collapsed")
            with col_btn:
                if st.button("🎙️", key="mic_btn"):
                    listening_placeholder.info("🎧 Đang nghe...")
                    voice_text, error = self.voice_controller.get_voice_query()
                    listening_placeholder.empty()
                    if error: listening_placeholder.warning(error)
                    else:
                        st.session_state["voice_query"] = voice_text
                        st.session_state["fill_from_voice"] = True
                        st.rerun()

        # --- UI TÌM KIẾM ---
        if search_query:
            with c1:
                st.markdown(f"##### 🔎 Kết quả tìm kiếm cho: *'{search_query}'*")
                recs = self.service.get_recommendations(search_query)
                if isinstance(recs, pd.DataFrame):
                    for _, row in recs.iterrows():
                        with st.container(border=True):
                            sc2, sc3 = st.columns([4, 1.5])
                            with sc2:
                                st.markdown(f"**{row['title']}**")
                                st.caption(f"⭐ {row['average_rating']:.1f} | {str(row['genres']).replace('|', ', ')}")
                            with sc3:
                                st.write("") # Spacer
                                if st.button("Đặt vé", key=f"s_btn_{row['movieId']}"):
                                    st.session_state['selected_movie_id'] = row['movieId']
                                    st.session_state['selected_seats'] = []
                                    st.session_state['page'] = 'booking'
                                    st.rerun()
                elif isinstance(recs, list) and recs:
                    st.warning(recs[0])

        movies = self.service.get_all_movies()
        items_per_slide = 5
        total_movies = len(movies)
        start_idx = st.session_state['movie_index']
        end_idx = min(start_idx + items_per_slide, total_movies)
        current_movies = movies[start_idx:end_idx]

        col_prev, col_main, col_next = st.columns([0.2, 10, 0.2])
        
        with col_prev:
            st.markdown("<br>"*8, unsafe_allow_html=True)
            if start_idx > 0 and st.button("❮", key="prev"):
                st.session_state['movie_index'] = max(0, start_idx - items_per_slide)
                st.rerun()

        with col_main:
            cols = st.columns(items_per_slide)
            for idx, movie in enumerate(current_movies):
                with cols[idx]:
                    if movie:
                        with st.container():
                            # Dùng HTML để render Card đẹp hơn
                            st.markdown(f"""
                                <div class="movie-container">
                                    <div class="movie-img-box"><img src="{movie.poster}"></div>
                                    <div class="movie-title" title="{movie.title}">{movie.title}</div>
                                    <div class="movie-meta">
                                        <span class="tag">{movie.genre.split(',')[0]}</span>
                                        <span style="float: right; color: #ffeb3b; font-weight: bold;">{movie.rating}</span>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            st.write("")
                            if st.button("ĐẶT VÉ", key=f"btn_{movie.id}", use_container_width=True):
                                st.session_state['selected_movie_id'] = movie.id
                                st.session_state['selected_seats'] = []
                                st.session_state['page'] = 'booking'
                                st.rerun()

        with col_next:
            st.markdown("<br>"*8, unsafe_allow_html=True)
            if end_idx < total_movies and st.button("❯", key="next"):
                st.session_state['movie_index'] += items_per_slide
                st.rerun()

    def render_booking(self):
        self.render_header()
        
        movie = self.service.get_movie_by_id(st.session_state['selected_movie_id'])

        if not movie:
            st.error("Không tìm thấy phim!")
            if st.button("Quay lại"):
                st.session_state['page'] = 'home'
                st.rerun()
            return

        if st.button("⬅ QUAY LẠI TRANG CHỦ", key="back_home"):
            st.session_state['page'] = 'home'
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_L, col_R = st.columns([1, 2], gap="large")

        with col_L:
            # INFO BOX
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
                    <div style="display: flex; gap: 20px; align-items: center;">
                        <img src="{movie.poster}" style="width: 110px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.5);">
                        <div>
                            <h2 style="margin: 0; font-size: 24px; background: linear-gradient(to right, #ff9966, #ff5e62); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{movie.title}</h2>
                            <p style="margin-top: 10px; font-size: 14px; color: #aaa;">⏱ Thời lượng: {movie.duration}<br>🎭 Thể loại: {movie.genre}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("### 📅 CHỌN SUẤT CHIẾU")
            days = list(self.service.showtimes.keys())
            s_day = st.selectbox("Chọn Ngày", days, label_visibility="collapsed")
            st.session_state['selected_date'] = s_day
            
            st.markdown("---")
            times = self.service.showtimes.get(s_day, [])
            s_time = st.radio("Chọn Giờ", times, horizontal=True)
            st.session_state['selected_time'] = s_time

            count = len(st.session_state['selected_seats'])
            total = count * movie.price
            
            # BILL BOX CAO CẤP
            st.markdown(f"""
            <div style="background: white; color: #333; padding: 25px; border-radius: 15px; margin-top: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 5px; background: linear-gradient(90deg, #ff416c, #ff4b2b);"></div>
                <div style="text-align: center; font-weight: 900; letter-spacing: 2px; font-size: 18px; margin-bottom: 20px; color: #16213e;">TICKET RECEIPT</div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #666;">Phim</span>
                    <strong style="color: #333;">{movie.title[:18]}...</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #666;">Ghế</span>
                    <strong style="color: #333;">{', '.join(st.session_state['selected_seats']) if count else '--'}</strong>
                </div>
                 <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #666;">Giá vé</span>
                    <strong style="color: #333;">{movie.price:,.0f} đ</strong>
                </div>
                <hr style="border-top: 2px dashed #ccc; margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 24px; font-weight: 800;">
                    <span style="color: #16213e;">TỔNG</span>
                    <span style="color: #ff4b2b;">{total:,.0f} đ</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if count > 0:
                st.write("")
                if st.button("💳 THANH TOÁN NGAY", type="primary", use_container_width=True):
                    if not st.session_state['is_logged_in']:
                        st.warning("⚠️ Bạn cần đăng nhập để thanh toán!")
                        et.sleep(1)
                        st.session_state['pre_login_page'] = 'booking'
                        st.session_state['page'] = 'login'
                        st.rerun()
                    else:
                        if not check_availability(movie.id, s_day, s_time, st.session_state['selected_seats']):
                            st.error("Ghế đã có người đặt!")
                        else:
                            save_booking(movie.id, s_day, s_time, st.session_state['selected_seats'])
                            st.session_state['selected_seats'] = []
                            st.balloons()
                            st.success(f"Cảm ơn {st.session_state['username']}! Vé đã được gửi tới email.")
                            et.sleep(2)
                            st.session_state['page'] = 'home'
                            st.rerun()

        with col_R:
            # MÀN HÌNH CONG
            st.markdown("""
                <div style="perspective: 1000px; margin-bottom: 40px; text-align: center;">
                    <div style="
                        width: 80%; margin: 0 auto; height: 10px; 
                        background: #fff; 
                        box-shadow: 0 20px 50px rgba(255,255,255,0.2); 
                        border-radius: 50%; 
                        transform: rotateX(-5deg);">
                    </div>
                    <div style="margin-top: 10px; color: #666; font-size: 12px; letter-spacing: 5px;">MÀN HÌNH</div>
                </div>
            """, unsafe_allow_html=True)
            
            layout = self.service.get_seat_layout(movie.id, st.session_state['selected_date'], st.session_state['selected_time'])
            
            with st.container():
                for r, row in enumerate(layout):
                    cols = st.columns([1.5] + [1]*8 + [1.5]) # Căn giữa lưới ghế
                    for c, status in enumerate(row):
                        seat_id = f"{chr(65 + r)}{c + 1}"
                        with cols[c+1]:
                            if status == 1: 
                                st.button(f"{seat_id}", key=seat_id, disabled=True)
                            elif seat_id in st.session_state['selected_seats']:
                                if st.button(f"✓ {seat_id}", key=seat_id, type="primary"):
                                    st.session_state['selected_seats'].remove(seat_id)
                                    st.rerun()
                            else:
                                if st.button(f"{seat_id}", key=seat_id):
                                    st.session_state['selected_seats'].append(seat_id)
                                    st.rerun()
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            xc1, xc2, xc3, xc4, xc5 = st.columns([1, 2, 2, 2, 1])
            with xc2: st.markdown("⬜ **Trống**")
            with xc3: st.markdown("🔒 **Đã đặt**")
            with xc4: st.markdown("🔴 **Đang chọn**")

    def run(self):
        if st.session_state['page'] == 'home':
            self.render_home()
        elif st.session_state['page'] == 'booking':
            self.render_booking()
        elif st.session_state['page'] == 'login':
            self.render_login()
        
        # Gọi Footer ở cuối mọi trang
        self.render_footer()

if __name__ == "__main__":
    app = CinemaAppUI()
    app.run()