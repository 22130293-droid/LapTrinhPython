import streamlit as st
import pandas as pd
import os
import random
import textwrap
import json
import hashlib

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="Start Cinema System", page_icon="🎬", layout="wide")

FILE_USERS = "users.json"
FILE_BOOKINGS = "bookings.json"
FILE_MOVIES = "data/movies.csv"
FILE_SHOWTIMES = "backend_module/data_structure.json"

EVENT_BANNERS = [
    "https://media.lottecinemavn.com/Media/WebAdmin/35faf5f79b8c43fa91450705f57b9b10.png",
    "https://media.lottecinemavn.com/Media/WebAdmin/4b2559e836174a7b973909774640498b.jpg",
    "https://media.lottecinemavn.com/Media/WebAdmin/b689028882744782928340d8544df201.jpg"
]

SNACK_MENU = {
    "combo_1": {"name": "Combo Solo", "price": 79000, "icon": "🍿🥤"},
    "combo_2": {"name": "Combo Đôi", "price": 109000, "icon": "🍿🥤🥤"},
}

# --- 2. AUTH SERVICE ---
class AuthService:
    def __init__(self):
        self.users = self.load_users()
    def load_users(self):
        if not os.path.exists(FILE_USERS): return {}
        try:
            with open(FILE_USERS, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    def save_users(self):
        with open(FILE_USERS, "w", encoding="utf-8") as f:
            json.dump(self.users, f, ensure_ascii=False, indent=4)
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    def register(self, username, password, fullname):
        if username in self.users: return False, "Tên đăng nhập đã tồn tại!"
        self.users[username] = {"password": self.hash_password(password), "fullname": fullname}
        self.save_users()
        return True, "Đăng ký thành công! Vui lòng đăng nhập."
    def login(self, username, password):
        if username not in self.users: return False, "Tên đăng nhập không tồn tại."
        if self.users[username]["password"] == self.hash_password(password):
            return True, self.users[username]["fullname"]
        return False, "Mật khẩu không chính xác."

# --- 3. DATA SERVICE ---
@st.cache_resource
def get_recommender_model():
    df_movies = pd.DataFrame()
    if os.path.exists(FILE_MOVIES):
        try: df_movies = pd.read_csv(FILE_MOVIES)
        except: pass
    return None, df_movies

class Movie:
    def __init__(self, id, title, genre, duration, rating, poster, price):
        self.id = id; self.title = title; self.genre = genre; self.duration = duration
        self.rating = rating; self.poster = poster; self.price = price

class CinemaService:
    def __init__(self):
        self.movies = []
        self.showtimes = {}
        self.recommender, self.df_full = get_recommender_model()
        self.load_movies_from_db() 
        self.load_showtimes_from_db()
        
        # Load booking history
        if 'booked_seats_db' not in st.session_state:
            st.session_state['booked_seats_db'] = self.load_bookings()

    def load_bookings(self):
        if os.path.exists(FILE_BOOKINGS):
            try:
                with open(FILE_BOOKINGS, "r", encoding="utf-8") as f: return json.load(f)
            except: pass
        return {"1_Hôm nay_19:00": ["D4", "D5"]} # Mock default

    def save_bookings(self):
        with open(FILE_BOOKINGS, "w", encoding="utf-8") as f:
            json.dump(st.session_state['booked_seats_db'], f, ensure_ascii=False, indent=4)

    def load_showtimes_from_db(self):
        if os.path.exists(FILE_SHOWTIMES):
            try:
                with open(FILE_SHOWTIMES, "r", encoding="utf-8") as f:
                    self.showtimes = json.load(f)
                    return
            except: pass
        self.showtimes = {
            "Hôm nay": ["09:30", "14:15", "19:00", "21:30"],
            "Ngày mai": ["10:00", "18:00", "20:00"]
        }

    def load_movies_from_db(self):
        if 'stored_movie_list' in st.session_state:
            self.movies = st.session_state['stored_movie_list']
            return

        if self.df_full is not None and not self.df_full.empty:
            for index, row in self.df_full.head(30).iterrows():
                m_id = row.get('movieId', index)
                title = row.get('title', 'Unknown')
                genres = str(row.get('genres', 'Unknown')).replace('|', ', ')
                price = 110000
                duration = "120 phút"
                rating = f"⭐ {row.get('average_rating', 8.5):.1f}"
                safe_title = title.split('(')[0].strip()
                poster = f"https://placehold.co/400x600/222/FFF.png?text={safe_title.replace(' ', '+')}&font=roboto"
                self.movies.append(Movie(m_id, title, genres, duration, rating, poster, price))
        else:
            titles = ["Jumanji", "Oppenheimer", "Barbie", "Conan", "Avatar 2", "Spider-Man", "Elemental", "Flash", "Transformers", "Insidious"]
            for i, title in enumerate(titles):
                self.movies.append(Movie(i + 1, title, "Hành Động", "120 phút", "⭐ 9.5", f"https://placehold.co/400x600/111/FFF.png?text={title}", 110000))
            
        st.session_state['stored_movie_list'] = self.movies

    def get_all_movies(self): return self.movies
    
    def get_movie_by_id(self, id):
        for m in self.movies:
            if m.id == id: return m
        return None

    def get_seat_layout(self, m_id, d, t):
        key = f"{m_id}_{d}_{t}"
        booked = st.session_state['booked_seats_db'].get(key, [])
        return [[1 if f"{chr(65 + r)}{c + 1}" in booked else 0 for c in range(8)] for r in range(6)]

    def book_seats(self, m_id, d, t, seats):
        key = f"{m_id}_{d}_{t}"
        if key not in st.session_state['booked_seats_db']: 
            st.session_state['booked_seats_db'][key] = []
        st.session_state['booked_seats_db'][key].extend(seats)
        self.save_bookings()

    def get_recommendations(self, title):
        results = []
        keyword = title.lower()
        for m in self.movies:
            if keyword in m.title.lower(): results.append(m)
        return results

# --- 4. UI VIEW ---
class CinemaAppUI:
    def __init__(self):
        self.auth_service = AuthService()
        self.service = CinemaService()
        self.init_state()
        self.inject_css()

    def init_state(self):
        defaults = {'page': 'home', 'current_user': None, 'movie_index': 0, 'selected_movie_id': None, 'selected_seats': [], 'selected_date': "Hôm nay", 'selected_time': "19:00", 'cart_snacks': {k: 0 for k in SNACK_MENU}}
        for k, v in defaults.items():
            if k not in st.session_state: st.session_state[k] = v

    def inject_css(self):
        st.markdown(textwrap.dedent("""
            <style>
            :root { --primary: #E50914; --bg: #111; --text: #FFF; --card-bg: #23263a; }
            .stApp { background-color: var(--bg) !important; font-family: 'Roboto', sans-serif; }
            header { visibility: hidden; }
            .main .block-container { padding-top: 1rem; }

            /* --- HEADER FIXED --- */
            .header-bg {
                position: fixed; top: 0; left: 0; right: 0; height: 70px;
                background: #000000; border-bottom: 2px solid var(--primary);
                z-index: 999; display: flex; align-items: center; padding: 0 40px;
            }
            .header-logo { 
                font-size: 24px; font-weight: 900; color: var(--primary); 
                text-decoration: none; text-transform: uppercase; letter-spacing: 1px;
                position: fixed; top: 18px; left: 40px; z-index: 10000;
            }
            
            /* --- MENU BUTTONS --- */
            .nav-container {
                position: fixed; top: 15px; right: 40px; z-index: 10000;
                display: flex; gap: 20px; align-items: center;
            }
            .nav-container button {
                background: transparent !important; border: none !important;
                color: #CCCCCC !important; text-transform: uppercase;
                font-weight: 700 !important; font-size: 14px !important;
                padding: 5px 10px !important; margin: 0 !important; box-shadow: none !important;
            }
            .nav-container button:hover { color: var(--primary) !important; text-decoration: none !important; }
            .nav-container button:focus { color: var(--primary) !important; border: none !important; background: transparent !important; }

            /* --- SEAT STYLES --- */
            /* 1. Ghế đã bán */
            button:disabled { background-color: #333 !important; color: #555 !important; border: 1px solid #444 !important; opacity: 1 !important; }
            
            /* 2. Ghế đang chọn (Primary = Đỏ đặc) */
            div[data-testid="column"] button[kind="primary"] {
                background-color: var(--primary) !important; border: 1px solid var(--primary) !important;
                color: white !important; font-weight: bold !important;
                box-shadow: 0 0 10px rgba(229, 9, 20, 0.8) !important; transform: scale(1.05); 
            }
            /* Giữ màu đỏ khi focus */
            div[data-testid="column"] button[kind="primary"]:focus,
            div[data-testid="column"] button[kind="primary"]:active {
                background-color: var(--primary) !important; color: white !important; border-color: var(--primary) !important;
            }

            /* 3. Ghế trống (Secondary = Viền đỏ) */
            div[data-testid="column"] button[kind="secondary"] {
                background-color: transparent !important; border: 1px solid var(--primary) !important; color: var(--primary) !important;
            }
            div[data-testid="column"] button[kind="secondary"]:hover {
                background-color: rgba(229, 9, 20, 0.15) !important; box-shadow: 0 0 8px rgba(229, 9, 20, 0.5) !important;
            }

            /* --- MOVIE CARD & SLIDER --- */
            .movie-card-box { background-color: var(--card-bg); border-radius: 8px; padding: 10px; border: 1px solid #333; height: 450px; display: flex; flex-direction: column; justify-content: space-between; }
            .poster-frame { width: 100%; aspect-ratio: 2/3; overflow: hidden; border-radius: 6px; background: #000; }
            .poster-frame img { width: 100%; height: 100%; object-fit: cover; }
            .movie-title { font-weight: bold; font-size: 15px; color: white; margin-top: 8px; margin-bottom: 5px; height: 40px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
            
            /* CSS Slider */
            input[name="slider"] { display: none; }
            .slider-frame { overflow: hidden; height: 450px; width: 100%; border-radius: 12px; position: relative; border: 1px solid #333; margin-bottom: 20px; }
            .slide-images { width: 300%; height: 100%; display: flex; transition: margin-left 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94); }
            .img-container { width: 100%; height: 100%; } .img-container img { width: 100%; height: 100%; object-fit: cover; }
            #slide-1:checked ~ .slider-frame .slide-images { margin-left: 0%; }
            #slide-2:checked ~ .slider-frame .slide-images { margin-left: -100%; }
            #slide-3:checked ~ .slider-frame .slide-images { margin-left: -200%; }
            .swiper-nav { display: flex; justify-content: center; gap: 15px; margin-bottom: 30px; }
            .thumb-box { width: 120px; height: 70px; border-radius: 6px; overflow: hidden; border: 2px solid #444; cursor: pointer; opacity: 0.6; transition: 0.3s; }
            .thumb-box:hover { opacity: 1; border-color: var(--primary); }
            .thumb-box img { width: 100%; height: 100%; object-fit: cover; }
            #slide-1:checked ~ .swiper-nav label.label-1 .thumb-box { border-color: var(--primary); opacity: 1; transform: scale(1.1); }
            #slide-2:checked ~ .swiper-nav label.label-2 .thumb-box { border-color: var(--primary); opacity: 1; transform: scale(1.1); }
            #slide-3:checked ~ .swiper-nav label.label-3 .thumb-box { border-color: var(--primary); opacity: 1; transform: scale(1.1); }

            /* --- MISC --- */
            .bill-box { background: #1a1a1a; padding: 20px; border-radius: 8px; border: 1px solid #333; }
            .auth-box { background: #23263a; padding: 40px; border-radius: 12px; border: 1px solid #444; width:100%; }
            .screen-glow { height: 4px; background: var(--primary); border-radius: 50%; box-shadow: 0 0 20px 5px var(--primary); opacity: 0.7; margin: 0 auto 30px auto; width: 80%; }
            div.stButton > button { background-color: var(--primary); color: white; border: none; font-weight: bold; border-radius: 4px; }
            
            /* Voice Button Style */
            div[data-testid="column"] button[key="mic_icon"] {
                background: transparent !important; border: 1px solid #444 !important;
                font-size: 20px; padding: 5px 10px !important;
            }
            </style>
        """), unsafe_allow_html=True)

    def render_header(self):
        st.markdown('<div class="header-bg"><div class="header-logo">🎬 START CINEMA</div></div>', unsafe_allow_html=True)
        st.markdown('<div style="height: 70px;"></div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="nav-container">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 1, 1.5]) 
            with c1: 
                if st.button("TRANG CHỦ", key="h_home"): st.session_state['page'] = 'home'; st.rerun()
            with c2: st.button("SỰ KIỆN", key="h_event")
            with c3: 
                user = st.session_state.get('current_user')
                label = "THÀNH VIÊN" if not user else f"👤 {user}"
                if st.button(label, key="h_auth"): st.session_state['page'] = 'auth'; st.rerun() 
            st.markdown('</div>', unsafe_allow_html=True)

    def render_auth(self):
        self.render_header()
        c1, c2, c3 = st.columns([3, 4, 3])
        with c2:
            st.markdown("<div class='auth-box'><h2 style='text-align:center; color:#E50914'>THÀNH VIÊN</h2>", unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["ĐĂNG NHẬP", "ĐĂNG KÝ"])
            with tab1:
                with st.form("login"):
                    u = st.text_input("Username")
                    p = st.text_input("Password", type="password")
                    if st.form_submit_button("LOGIN"):
                        s, m = self.auth_service.login(u, p)
                        if s: st.session_state['current_user']=m; st.session_state['page']='home'; st.rerun()
                        else: st.error(m)
            with tab2:
                with st.form("reg"):
                    u = st.text_input("New User")
                    p = st.text_input("New Pass", type="password")
                    f = st.text_input("Name")
                    if st.form_submit_button("REGISTER"):
                        s, m = self.auth_service.register(u, p, f)
                        if s: st.success(m)
                        else: st.error(m)
            st.markdown("</div>", unsafe_allow_html=True)

    def render_banner_swiper(self):
        inputs = "".join([f'<input type="radio" name="slider" id="slide-{i+1}" {"checked" if i==0 else ""}>' for i in range(3)])
        imgs = "".join([f'<div class="img-container"><img src="{url}"></div>' for url in EVENT_BANNERS])
        thumbs = "".join([f'<label for="slide-{i+1}" class="label-{i+1}"><div class="thumb-box"><img src="{url}"></div></label>' for i, url in enumerate(EVENT_BANNERS)])
        st.markdown(f"""
            <div style="position: relative;">
                {inputs}
                <div class="slider-frame">
                    <div class="slide-images">{imgs}</div>
                    <div style="position: absolute; bottom: 0; left: 0; width: 100%; height: 100px; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); pointer-events: none;"></div>
                </div>
                <div class="swiper-nav">{thumbs}</div>
            </div>
        """, unsafe_allow_html=True)

    def render_home(self):
        self.render_header()
        self.render_banner_swiper()

        if not self.service.movies: st.error("❌ No data available."); return

        st.subheader("🔥 PHIM ĐANG CHIẾU")
        
        # --- TÌM KIẾM + VOICE ICON ---
        c_search, c_mic = st.columns([8, 1])
        with c_search:
            search = st.text_input("Search", placeholder="Tìm tên phim...", label_visibility="collapsed")
        with c_mic:
            if st.button("🎙️", key="mic_icon", help="Tìm bằng giọng nói"):
                st.toast("Đang lắng nghe...", icon="🎤")

        movies = self.service.get_recommendations(search) if search else self.service.get_all_movies()
        if not movies: st.warning("Không tìm thấy.")
        
        # SEARCH LIST VIEW
        if search:
             for movie in movies:
                with st.container():
                    st.markdown(f"""
                        <div style="background:#23263a; padding:15px; border-radius:8px; margin-bottom:10px; border:1px solid #333; display:flex; gap:20px;">
                            <img src="{movie.poster}" style="width:100px; height:150px; object-fit:cover; border-radius:4px;">
                            <div style="flex-grow:1;">
                                <h4 style="margin:0; color:white;">{movie.title}</h4>
                                <p style="color:#aaa; font-size:14px;">{movie.genre} | {movie.duration} | {movie.rating}</p>
                                <h4 style="color:#E50914;">{movie.price:,.0f} VND</h4>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("ĐẶT NGAY", key=f"s_btn_{movie.id}"):
                        st.session_state['selected_movie_id'] = movie.id; st.session_state['selected_seats'] = []; st.session_state['page'] = 'booking'; st.rerun()
        else:
            # GRID CAROUSEL
            items_per_slide = 5 
            total_movies = len(movies)
            col_prev, col_display, col_next = st.columns([0.5, 10, 0.5])
            
            with col_prev:
                st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
                if st.session_state['movie_index'] > 0:
                    if st.button("◀", key="prev_slide"):
                        st.session_state['movie_index'] = max(0, st.session_state['movie_index'] - items_per_slide); st.rerun()
            
            with col_display:
                start_idx = st.session_state['movie_index']
                end_idx = min(start_idx + items_per_slide, total_movies)
                cols = st.columns(items_per_slide)
                
                for idx, movie in enumerate(movies[start_idx:end_idx]):
                    with cols[idx]:
                        st.markdown(f"""
                            <div class="movie-card-box">
                                <div class="poster-frame"><img src="{movie.poster}"></div>
                                <div class="movie-info">
                                    <div class="movie-title">{movie.title}</div>
                                    <div style="display:flex; justify-content:space-between; font-size:12px; color:#aaa;">
                                        <span>{movie.genre}</span><span>{movie.rating}</span>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("ĐẶT VÉ", key=f"grid_btn_{movie.id}", type="primary"):
                            st.session_state['selected_movie_id'] = movie.id
                            st.session_state['selected_seats'] = []
                            st.session_state['page'] = 'booking'; st.rerun()
            
            with col_next:
                st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
                if end_idx < total_movies:
                    if st.button("▶", key="next_slide"):
                        st.session_state['movie_index'] += items_per_slide; st.rerun()

    def render_booking(self):
        movie = self.service.get_movie_by_id(st.session_state['selected_movie_id'])
        if not movie: st.session_state['page']='home'; st.rerun(); return

        self.render_header()
        st.markdown("<br>", unsafe_allow_html=True)
        cL, cR = st.columns([1.5, 3])

        with cL:
            c1, c2 = st.columns([1, 1.5])
            c1.image(movie.poster, use_container_width=True)
            with c2:
                st.markdown(f"### {movie.title}")
                st.write(f"🏷️ **{movie.price:,.0f} VND**")
            d = st.selectbox("Ngày:", list(self.service.showtimes.keys()))
            st.session_state['selected_date'] = d
            t = st.radio("Suất chiếu:", self.service.showtimes[d], horizontal=True)
            st.session_state['selected_time'] = t
            st.markdown("<div class='bill-box'>", unsafe_allow_html=True)
            seats = st.session_state['selected_seats']
            total = len(seats) * movie.price
            st.write(f"Ghế: {', '.join(seats) if seats else '---'}")
            st.markdown(f"<h3 style='color:#E50914'>{total:,.0f} VND</h3>", unsafe_allow_html=True)
            if seats:
                if st.button("THANH TOÁN NGAY", type="primary"):
                    if not st.session_state.get('current_user'):
                        st.warning("Vui lòng đăng nhập!"); st.session_state['page']='auth'; st.rerun()
                    else:
                        self.service.book_seats(movie.id, d, t, seats)
                        st.success("Thành công!"); st.session_state['selected_seats']=[]; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with cR:
            st.subheader("MÀN HÌNH")
            st.markdown("<div class='screen-glow'></div>", unsafe_allow_html=True)
            layout = self.service.get_seat_layout(movie.id, st.session_state['selected_date'], st.session_state['selected_time'])
            
            for r, row in enumerate(layout):
                cols = st.columns(8)
                char = chr(65 + r)
                for c, status in enumerate(row):
                    seat_id = f"{char}{c+1}"
                    with cols[c]:
                        if status == 1:
                            st.button(f"{seat_id}", key=seat_id, disabled=True)
                        else:
                            is_selected = seat_id in st.session_state['selected_seats']
                            btn_type = "primary" if is_selected else "secondary"
                            # div seat-container chỉ để giữ form, style chính nằm ở button[kind=...]
                            st.markdown('<div class="seat-container">', unsafe_allow_html=True)
                            if st.button(f"{seat_id}", key=seat_id, type=btn_type):
                                if is_selected: st.session_state['selected_seats'].remove(seat_id)
                                else: st.session_state['selected_seats'].append(seat_id)
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
            st.write("")
            cm1, cm2, cm3 = st.columns(3)
            cm1.markdown("🟦 **Ghế trống** (Viền đỏ)")
            cm2.markdown("🟥 **Đang chọn** (Đỏ đặc)")
            cm3.markdown("⬛ **Đã bán** (Xám)")

    def run(self):
        if st.session_state['page'] == 'auth': self.render_auth()
        elif st.session_state['page'] == 'booking': self.render_booking()
        else: self.render_home()

if __name__ == "__main__":
    app = CinemaAppUI()
    app.run()