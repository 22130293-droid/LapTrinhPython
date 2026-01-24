import streamlit as st
import pandas as pd
import os
import random
import sys

# --- XỬ LÝ ĐƯỜNG DẪN HỆ THỐNG ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from config import FILE_IMAGES, POSTER_PLACEHOLDER
from .models import Movie

# --- IMPORT CÁC MODULE AI & BOOKING ---
try:
    from movie_recommender_ai_module.data_processor import load_data
    from movie_recommender_ai_module.recommender import ContentBasedRecommender
    from booking_and_voice_search.booking_serveice import load_booking_data
except ImportError as e:
    st.error(f"Lỗi cấu trúc thư mục hoặc thiếu file: {e}")


def _create_movie_from_row(row):
    """Chuyển đổi dữ liệu thô (Series, Dict) sang đối tượng Movie"""
    img_link = POSTER_PLACEHOLDER

    # Kiểm tra cột poster_url
    if 'poster_url' in row and pd.notna(row['poster_url']) and str(row['poster_url']).strip() != "":
        img_link = row['poster_url']
    else:
        safe_title = str(row['title']).split('(')[0].strip().replace(' ', '+')
        img_link = f"https://placehold.co/400x600?text={safe_title}"

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


@st.cache_resource
def get_cached_data():
    df_movies = load_data()
    recommender = None
    movies_list_ui = []

    if not df_movies.empty:
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

        recommender = ContentBasedRecommender(df_movies)

        for index, row in df_movies.head(50).iterrows():
            movies_list_ui.append(_create_movie_from_row(row))

    return recommender, movies_list_ui, df_movies


class CinemaService:
    def __init__(self):
        self.showtimes = {
            "Hôm nay": ["09:30", "11:00", "14:15", "19:00", "21:30", "23:00"],
            "Ngày mai": ["10:00", "13:00", "18:00", "20:00"],
            "Ngày kia": ["09:00", "15:00", "19:30"]
        }
        self.recommender, self.movies, self.full_df = get_cached_data()

    def get_all_movies(self):
        return self.movies

    def get_movie_by_id(self, id):
        for m in self.movies:
            if m.id == id: return m
        if not self.full_df.empty:
            row = self.full_df[self.full_df['movieId'] == id]
            if not row.empty:
                return _create_movie_from_row(row.iloc[0])
        return None

    # Thêm vào class MovieService trong core/services.py
    def get_personalized_recommendations(self, user_id, num_recommendations=10):
        from booking_and_voice_search.booking_serveice import get_user_history_json

        # 1. Lấy lịch sử đặt vé của user
        history = get_user_history_json(user_id)

        if not history:
            # Nếu chưa mua vé nào, gợi ý phim có điểm cao nhất (Top Trending)
            return self.full_df.sort_values(by='average_rating', ascending=False).head(num_recommendations)

        # 2. Lấy danh sách các movieId đã đặt (không trùng lặp)
        booked_movie_ids = list(set([int(t['movie_id']) for t in history]))

        # 3. Gọi module AI để lấy danh sách gợi ý
        # Giả sử recommender của ông có hàm get_recommendations_multiple
        try:
            from movie_recommender_ai_module.recommender import ContentBasedRecommender
            recommender = ContentBasedRecommender(self.full_df)

            # Lấy gợi ý dựa trên bộ phim cuối cùng họ mua (hoặc tất cả)
            last_movie_id = booked_movie_ids[-1]
            recommended_ids = recommender.get_recommendations(last_movie_id, top_n=num_recommendations)

            # Lọc ra thông tin phim từ full_df
            return self.full_df[self.full_df['movieId'].isin(recommended_ids)]
        except Exception as e:
            print(f"AI Error: {e}")
            return self.full_df.head(num_recommendations)

    def get_recommendations(self, movie_title, top_n=10):
        """Trả về tuple: (Danh sách phim tìm thấy, Danh sách phim AI gợi ý)"""
        if self.recommender is None or self.full_df.empty:
            return [], []

        # 1. TÌM KIẾM CHÍNH XÁC/GẦN ĐÚNG TRONG DATABASE
        search_mask = self.full_df['title'].str.contains(movie_title, case=False, na=False)
        search_df = self.full_df[search_mask].head(3)  # Lấy tối đa 3 kết quả khớp tên
        search_results = [_create_movie_from_row(row) for _, row in search_df.iterrows()]

        # 2. LẤY GỢI Ý TỪ AI
        ai_recs = []
        try:
            if hasattr(self.recommender, 'get_recommendations'):
                raw_result = self.recommender.get_recommendations(movie_title, top_n=top_n)
            else:
                raw_result = self.recommender.recommend(movie_title, top_n=top_n)

            # Chuyển đổi kết quả AI thành list Movie
            if isinstance(raw_result, pd.DataFrame):
                ai_recs = [_create_movie_from_row(row) for _, row in raw_result.iterrows()]
            elif isinstance(raw_result, list):
                for item in raw_result:
                    if hasattr(item, 'rating'):
                        ai_recs.append(item)
                    elif isinstance(item, (pd.Series, dict)):
                        ai_recs.append(_create_movie_from_row(item))
        except Exception:
            ai_recs = []

        return search_results, ai_recs

    def get_seat_layout(self, m_id, d, t):
        from booking_and_voice_search.booking_serveice import load_booking_data
        data = load_booking_data()
        m_id = str(m_id)

        # 1. Lấy danh sách thô (List of Dicts) từ JSON
        raw_booked = data.get("movies", {}).get(m_id, {}).get("showtimes", {}).get(d, {}).get(t, {}).get("booked_seats",
                                                                                                         [])

        # 2. TRÍCH XUẤT: Chuyển list Dict thành list String (chỉ lấy mã ghế)
        # Nếu b là dict thì lấy b["seat"], nếu đã là string thì giữ nguyên
        booked_codes = [b["seat"] if isinstance(b, dict) else b for b in raw_booked]

        # 3. SO SÁNH: Bây giờ lệnh 'in' sẽ hoạt động chuẩn xác
        return [[1 if f"{chr(65 + r)}{c + 1}" in booked_codes else 0 for c in range(8)] for r in range(6)]


class AdminService:
    def __init__(self, full_df):
        self.df = full_df
        self.json_path = os.path.join("booking_and_voice_search", "data_structure.json")

    def get_genre_distribution(self):
        if self.df.empty: return pd.Series()
        genres = self.df['genres'].str.split('|').explode()
        return genres.value_counts().head(10)

    def get_rating_stats(self):
        if self.df.empty: return pd.DataFrame()
        temp_df = self.df.copy()
        temp_df['rating_round'] = temp_df['average_rating'].round()
        return temp_df['rating_round'].value_counts().sort_index()

    def get_booking_stats(self):
        data = load_booking_data()
        total_revenue = 0
        total_tickets = 0
        movie_summary = []
        daily_summary = {}

        movies = data.get("movies", {})
        for m_id, m_data in movies.items():
            m_rev, m_tix = 0, 0
            showtimes = m_data.get("showtimes", {})
            for date, times in showtimes.items():
                if date not in daily_summary:
                    daily_summary[date] = {"revenue": 0, "tickets": 0}

                for time, slot in times.items():
                    booked = slot.get("booked_seats", [])
                    for ticket in booked:
                        price = ticket.get("price", 105000)
                        total_revenue += price
                        m_rev += price
                        total_tickets += 1
                        m_tix += 1
                        # Gom nhóm theo ngày
                        daily_summary[date]["revenue"] += price
                        daily_summary[date]["tickets"] += 1

            if m_tix > 0:
                movie_summary.append({"movie_id": m_id, "tickets": m_tix, "revenue": m_rev})

        return total_revenue, total_tickets, movie_summary, daily_summary