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

# Ảnh mặc định
POSTER_PLACEHOLDER = "https://placehold.co/400x600/png?text=No+Poster&font=roboto"

# Danh sách ảnh Banner
EVENT_BANNERS = [
    "https://www.cgv.vn/media/banner/cache/1/b58515f018eb873dafa430b6f9ae0c1e/9/8/980x448_17__5.jpg",
    "https://media.lottecinemavn.com/Media/WebAdmin/4b2559e836174a7b973909774640498b.jpg",
    "https://media.lottecinemavn.com/Media/WebAdmin/b689028882744782928340d8544df201.jpg"
]


# --- 2. LỚP ĐỐI TƯỢNG (MODEL) ---
class Movie:
    def __init__(self, id, title, genre, duration, rating, poster, price):
        self.id = id
        self.title = title
        self.genre = genre
        self.duration = duration
        self.rating = rating
        self.poster = poster
        self.price = price


# Helper function: Dùng cache để model chỉ train 1 lần khi ứng dụng khởi động (Tối ưu hiệu suất)
@st.cache_resource
def get_recommender_model():
    """Tải dữ liệu đã merge và huấn luyện mô hình AI (Chỉ chạy 1 lần)."""
    # Hàm load_data đã tự động kiểm tra cache (cleaned_data.csv) và merge 3 file
    df_movies = load_data()
    if not df_movies.empty:
        # Khởi tạo mô hình ContentBasedRecommender
        recommender = ContentBasedRecommender(df_movies)
        return recommender, df_movies
    return None, pd.DataFrame()


# --- 3. LỚP XỬ LÝ DỮ LIỆU & DỊCH VỤ (SERVICE) ---
class CinemaService:
    def __init__(self):
        self.movies = []
        self.showtimes = {}
        self.booked_seats_db = {}

        # Tải mô hình đã được cache và DataFrame đã xử lý
        self.recommender, df_movies = get_recommender_model()
        self.load_movies_for_frontend(df_movies)  # Populate Movie objects từ DataFrame đã xử lý
        self.load_or_build_virtual_backend()  # Logic lịch chiếu và ghế ảo (Giữ nguyên)

    def load_movies_for_frontend(self, df):
        """Sử dụng DataFrame đã được merge/xử lý (có ratings, tags) để populate các đối tượng Movie."""
        if not df.empty:
            # Chỉ hiển thị 30 phim hàng đầu trên trang chủ
            for index, row in df.head(30).iterrows():
                # LẤY DỮ LIỆU THẬT: genres và average_rating/rating_count
                genres = str(row['genres']).replace('|', ', ')
                rating_display = f"⭐ {row['average_rating']:.1f} ({row['rating_count']} votes)"  # Hiển thị rating thật

                # Các thông tin khác vẫn dùng ảo vì không có trong dataset MovieLens
                random_price = random.choice([90000, 105000, 120000, 150000])
                random_duration = f"{random.randint(90, 160)} phút"

                # Tạo URL Poster động
                safe_title = str(row['title']).split('(')[0].strip().replace(' ', '+')
                poster_url = f"https://placehold.co/400x600?text={safe_title}"

                movie = Movie(
                    id=row['movieId'],
                    title=row['title'],
                    genre=genres,
                    duration=random_duration,
                    rating=rating_display,  # Dùng rating thật đã được merge
                    poster=poster_url,
                    price=random_price
                )
                self.movies.append(movie)

        if not self.movies:
            self.movies = [Movie(1, "Phim Demo", "Hành động", "120p", "C18", POSTER_PLACEHOLDER, 100000)]

    def load_or_build_virtual_backend(self):
        # (Giữ nguyên logic lịch chiếu và ghế ảo của TV2)
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
        for m in self.movies:
            if m.id == id: return m
        return None

    def get_seat_layout(self, m_id, d, t):
        data = load_booking_data()
        m_id = str(m_id)

        booked = (
            data.get("movies", {})
                .get(m_id, {})
                .get("showtimes", {})
                .get(d, {})
                .get(t, {})
                .get("booked_seats", [])
        )

        return [
            [1 if f"{chr(65 + r)}{c + 1}" in booked else 0 for c in range(8)]
            for r in range(6)
        ]


    def get_recommendations(self, title):
        """Hàm gọi thuật toán gợi ý từ module AI của TV1 (đã được cache)."""
        if self.recommender:
            return self.recommender.get_recommendations(title)
        return []


# --- 4. LỚP GIAO DIỆN (VIEW) ---
class CinemaAppUI:
    def __init__(self):
        self.service = CinemaService()
        self.inject_custom_css()
        self.voice_controller = VoiceSearchController()


        # State Management
        if 'page' not in st.session_state: st.session_state['page'] = 'home'
        if "voice_query" not in st.session_state:st.session_state["voice_query"] = ""
        if "fill_from_voice" not in st.session_state:st.session_state["fill_from_voice"] = False
        if 'movie_index' not in st.session_state: st.session_state['movie_index'] = 0
        if 'selected_movie_id' not in st.session_state: st.session_state['selected_movie_id'] = None
        if 'selected_seats' not in st.session_state: st.session_state['selected_seats'] = []
        if 'selected_date' not in st.session_state: st.session_state['selected_date'] = "Hôm nay"
        if 'selected_time' not in st.session_state: st.session_state['selected_time'] = "19:00"

    def inject_custom_css(self):
        st.markdown("""
            <style>
            /* 1. NỀN & FONT CHUNG */
            .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Helvetica', sans-serif; }
            h1, h2, h3 { color: #FFFFFF !important; }
            p, label, span { color: #E0E0E0 !important; }

            /* 2. HEADER */
            .header-container {
                display: flex; justify-content: space-between; align-items: center;
                padding: 15px 20px; background-color: #111; 
                border-bottom: 3px solid #E50914; margin-bottom: 20px;
            }
            .logo { font-size: 28px; font-weight: 900; color: #E50914 !important; text-transform: uppercase; text-decoration: none !important; }
            .nav-item { color: #FFF !important; margin-left: 20px; font-weight: bold; text-decoration: none !important; transition: 0.3s; }
            .nav-item:hover { color: #E50914 !important; }
            .header-container a { text-decoration: none !important; border-bottom: none !important; }

            /* 3. EVENT SLIDESHOW */
            .slider-frame {
                overflow: hidden; height: 400px; width: 100%; margin-bottom: 30px; border-radius: 12px;
                position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.8);
            }
            .slide-images { width: 300%; height: 100%; display: flex; animation: slide_animation 15s infinite; }
            .img-container { width: 100%; height: 100%; }
            .img-container img { width: 100%; height: 100%; object-fit: cover; }
            @keyframes slide_animation {
                0% { margin-left: 0%; } 30% { margin-left: 0%; } 33% { margin-left: -100%; }
                63% { margin-left: -100%; } 66% { margin-left: -200%; } 96% { margin-left: -200%; } 100% { margin-left: 0%; }
            }

            /* 4. MOVIE CARD */
            .movie-title { color: #FFD700 !important; font-size: 16px; font-weight: bold; margin-top: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .movie-meta { color: #BBB !important; font-size: 12px; }

            /* 5. BUTTONS STANDARD */
            div.stButton > button {
                background-color: #E50914; color: white; border: none; font-weight: bold; transition: 0.3s;
            }
            div.stButton > button:hover { background-color: #B20710; transform: scale(1.05); }

            /* 6. CUSTOM NEXT/PREV BUTTONS (MŨI TÊN TO) */
            /* Căn chỉnh nút mũi tên to ra và nằm giữa */
            div[data-testid="column"]:nth-of-type(1) div.stButton > button,
            div[data-testid="column"]:nth-of-type(3) div.stButton > button {
                background-color: transparent !important;
                color: rgba(255, 255, 255, 0.4) !important;
                font-size: 50px !important;
                border: none !important;
                padding: 0px !important;
                height: 100px !important;
                line-height: 1 !important;
                margin-top: 20px; /* Tinh chỉnh vị trí */
            }
            div[data-testid="column"]:nth-of-type(1) div.stButton > button:hover,
            div[data-testid="column"]:nth-of-type(3) div.stButton > button:hover {
                color: #E50914 !important;
                transform: scale(1.2) !important;
            }

            /* 7. BOOKING SCREEN */
            .bill-box { background-color: #1A1A1A; padding: 20px; border: 1px solid #333; border-radius: 8px; }
            .screen { 
                background: linear-gradient(180deg, #FFF 0%, rgba(255,255,255,0) 80%);
                height: 50px; opacity: 0.2; width: 80%; margin: 0 auto; 
                transform: perspective(600px) rotateX(-20deg);
                box-shadow: 0 20px 50px rgba(255,255,255,0.2);
            }
            </style>
        """, unsafe_allow_html=True)

    def render_header(self):
        st.markdown("""
            <div class="header-container">
                <a href="#" class="logo">🎬 START CINEMA</a>
                <div>
                    <a href="#" class="nav-item">TRANG CHỦ</a>
                    <a href="#" class="nav-item">SỰ KIỆN</a>
                    <a href="#" class="nav-item">THÀNH VIÊN</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    def render_event_slideshow(self):
        imgs_html = "".join([f'<div class="img-container"><img src="{url}"></div>' for url in EVENT_BANNERS])
        st.markdown(f"""
            <div class="slider-frame">
                <div class="slide-images">{imgs_html}</div>
                <div style="position: absolute; bottom: 20px; left: 30px; text-shadow: 2px 2px 4px black;">
                    <h2 style="font-size: 40px; margin:0; color: #FFF;">HOT EVENTS</h2>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- KHẮC PHỤC: HÀM RENDER HOME (ĐÃ ĐƯỢC ĐẶT TRONG CLASS) ---
    
    def render_home(self):
        
        self.render_header()
        self.render_event_slideshow()

        #Hiển thị thanh nhận diện giọng nói
        listening_placeholder = st.empty()

        if st.session_state.get("fill_from_voice"):
            st.session_state["manual_search_input"] = st.session_state["voice_query"]
            st.session_state["fill_from_voice"] = False

        c1, c2 = st.columns([3, 1])
        c1.subheader("🔥 PHIM ĐANG CHIẾU")

        # --- CHỨC NĂNG TÌM KIẾM/GỢI Ý (ĐÃ THÊM ICON MICRO) ---
        # Chia cột c2 thành hai phần: Input và Icon
          #HÀM ĐỒNG BỘ GIỌNG NÓI → INPUT (PHẢI ĐẶT TRƯỚC text_input)
      
        col_input, col_mic = c2.columns([4, 1])
        
      
        # 1. Thanh nhập liệu (chiếm 80% cột c2)
        search_query = col_input.text_input(
            "Tìm kiếm/Gợi ý phim:",
            placeholder="Nhập tên phim...",
            key="manual_search_input",
            label_visibility="collapsed"
        )

        # 2. Icon Micro (chiếm 20% cột c2)
        with col_mic:
            if st.button("🎙️", key="mic_icon"):
                listening_placeholder.info("🎧 Đang nghe giọng nói...")
                voice_text, error = self.voice_controller.get_voice_query()
                listening_placeholder.empty() 

                if error:
                    listening_placeholder.warning(f" {error}")
                else:
                    st.session_state["voice_query"] = voice_text
                    st.session_state["fill_from_voice"] = True
                    st.rerun()
          


        # --- LOGIC GỌI AI VÀ HIỂN THỊ KẾT QUẢ (GIỮ NGUYÊN) ---
        if search_query:

            # Gọi hàm get_recommendations đã được tích hợp (từ module của Thành viên 1)
            recommendations_df = self.service.get_recommendations(search_query)
            # 2. Hiển thị Kết quả Gợi ý (Ở cột lớn c1)
            if isinstance(recommendations_df, pd.DataFrame):                # Tiêu đề gợi ý
                c1.markdown(f"#### ✨ Top gợi ý cho '{search_query}':")                # Hiển thị danh sách kết quả
                for _, row in recommendations_df.iterrows():
                    # Lấy thông tin từ các cột trong DataFrame
                    r_title = row['title']
                    # Chuyển Action|Adventure thành Action, Adventure
                    r_genres = str(row['genres']).replace('|', ', ')
                    r_rating = row['average_rating']
                    r_votes = int(row['rating_count'])

                    # HIỂN THỊ CHI TIẾT
                    c1.markdown(f"**{r_title}**")
                    c1.caption(f"↳ 🎭 {r_genres} | ⭐ {r_rating:.1f}/5 ({r_votes:,} votes)")

                c1.markdown("---")  # Dấu phân cách


            elif isinstance(recommendations_df, list) and len(recommendations_df) > 0:
                c1.warning(recommendations_df[0])

        # --- END CHỨC NĂNG TÌM KIẾM/GỢI Ý ---

        movies = self.service.get_all_movies()
        items_per_slide = 5
        total_movies = len(movies)

        # Chia 3 cột: [Nút Trái] -- [Danh sách Phim] -- [Nút Phải]
        col_prev, col_display, col_next = st.columns([0.5, 10, 0.5])

        # Nút Trái
        with col_prev:
            st.markdown("<div style='height: 180px;'></div>", unsafe_allow_html=True)  # Spacer đẩy nút xuống giữa
            if st.session_state['movie_index'] > 0:
                if st.button("◀", key="prev_btn"):
                    st.session_state['movie_index'] = max(0, st.session_state['movie_index'] - items_per_slide)
                    st.rerun()

        # Danh sách phim
        with col_display:
            start_idx = st.session_state['movie_index']
            end_idx = min(start_idx + items_per_slide, total_movies)
            current_movies = movies[start_idx:end_idx]

            cols = st.columns(items_per_slide)
            for idx, movie in enumerate(current_movies):
                with cols[idx]:
                    if movie is None: continue  # Fix lỗi NoneType

                    with st.container():
                        poster = movie.poster if movie.poster else POSTER_PLACEHOLDER
                        st.markdown(f"""
                            <div style="border-radius: 8px; overflow: hidden; margin-bottom: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                                <img src="{poster}" style="width: 100%; aspect-ratio: 2/3; object-fit: cover;">
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"<div class='movie-title' title='{movie.title}'>{movie.title}</div>",
                                    unsafe_allow_html=True)
                        st.markdown(f"<div class='movie-meta'>{movie.genre}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='movie-meta'>⭐ {movie.rating} | ⏱ {movie.duration}</div>",
                                    unsafe_allow_html=True)

                        st.write("")
                        if st.button("ĐẶT VÉ", key=f"btn_{movie.id}"):
                            st.session_state['selected_movie_id'] = movie.id
                            st.session_state['selected_seats'] = []
                            st.session_state['page'] = 'booking'
                            st.rerun()

            st.caption(f"Hiển thị {start_idx + 1} - {end_idx} trên tổng số {total_movies} phim")

        # Nút Phải
        with col_next:
            st.markdown("<div style='height: 180px;'></div>", unsafe_allow_html=True)  # Spacer đẩy nút xuống giữa
            if end_idx < total_movies:
                if st.button("▶", key="next_btn"):
                    st.session_state['movie_index'] += items_per_slide
                    st.rerun()

    # --- HÀM RENDER BOOKING (ĐÃ ĐƯỢC ĐẶT TRONG CLASS) ---
    def render_booking(self):
        self.render_header()
        movie = self.service.get_movie_by_id(st.session_state['selected_movie_id'])

        if not movie:
            st.error("Không tìm thấy phim!")
            if st.button("Quay lại"):
                st.session_state['page'] = 'home'
                st.rerun()
            return

        if st.button("⬅️ QUAY LẠI TRANG CHỦ", key="back_home"):
            st.session_state['page'] = 'home'
            st.rerun()

        st.markdown("---")
        col_L, col_R = st.columns([1.2, 2.5])

        # CỘT TRÁI
        with col_L:
            c1, c2 = st.columns([1, 1.5])
            c1.image(movie.poster, use_container_width=True)
            with c2:
                st.markdown(f"### {movie.title}")
                st.caption(f"Thể loại: {movie.genre}")
                st.caption(f"Thời lượng: {movie.duration}")

            st.markdown("---")
            st.write("📅 **NGÀY & GIỜ CHIẾU**")

            days = list(self.service.showtimes.keys())
            s_day = st.selectbox("Ngày:", days, label_visibility="collapsed")
            st.session_state['selected_date'] = s_day

            times = self.service.showtimes.get(s_day, [])
            s_time = st.radio("Giờ:", times, horizontal=True)
            st.session_state['selected_time'] = s_time

            st.markdown("<br><div class='bill-box'>", unsafe_allow_html=True)
            st.markdown("#### 🧾 HÓA ĐƠN")
            count = len(st.session_state['selected_seats'])
            total = count * movie.price
            st.write(f"Vé: {count} x {movie.price:,.0f} đ")
            st.markdown(f"<h3 style='color:#E50914 !important'>TỔNG: {total:,.0f} đ</h3>", unsafe_allow_html=True)

            if count > 0:
                if st.button("THANH TOÁN NGAY", type="primary"):

                    movie_id = movie.id
                    date = st.session_state['selected_date']
                    time = st.session_state['selected_time']
                    seats = st.session_state['selected_seats']

                    # 1 Kiểm tra ghế
                    if not check_availability(movie_id, date, time, seats):
                        st.error(" Một số ghế đã được người khác đặt. Vui lòng chọn lại.")
                        return

                    # 2 Lưu booking
                    save_booking(movie_id, date, time, seats)

                    # 3 Reset state
                    st.session_state['selected_seats'] = []
                    st.balloons()
                    st.success("🎉 Đặt vé thành công!")
                    et.sleep(2)
                    st.rerun()
            # else:
            #     # st.info("Vui lòng chọn ghế bên phải")
            #     st.markdown("</div>", unsafe_allow_html=True)

        # CỘT PHẢI
        with col_R:
            st.subheader("SƠ ĐỒ GHẾ NGỒI")
            st.markdown("<div class='screen'>MÀN HÌNH</div><br>", unsafe_allow_html=True)
            layout = self.service.get_seat_layout(movie.id, st.session_state['selected_date'],
                                                  st.session_state['selected_time'])

            for r, row in enumerate(layout):
                cols = st.columns(8)
                for c, status in enumerate(row):
                    seat_id = f"{chr(65 + r)}{c + 1}"
                    with cols[c]:
                        if status == 1:
                            st.button("❌", key=seat_id, disabled=True)
                        elif seat_id in st.session_state['selected_seats']:
                            if st.button("✅", key=seat_id, type="primary"):
                                st.session_state['selected_seats'].remove(seat_id)
                                st.rerun()
                        else:
                            if st.button("⬜", key=seat_id):
                                st.session_state['selected_seats'].append(seat_id)
                                st.rerun()
            st.markdown("---")
            xc1, xc2, xc3 = st.columns(3)
            xc1.markdown("⬜ **Ghế trống**")
            xc2.markdown("❌ **Đã bán**")
            xc3.markdown("✅ **Đang chọn**")

    def run(self):
        if st.session_state['page'] == 'home':
            self.render_home()
        elif st.session_state['page'] == 'booking':
            self.render_booking()


if __name__ == "__main__":
    app = CinemaAppUI()
    app.run()
