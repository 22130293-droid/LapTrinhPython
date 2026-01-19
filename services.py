# Xử lý dữ liệu, logic backend ảo
import streamlit as st
import pandas as pd
import os
import random
from config import FILE_IMAGES, POSTER_PLACEHOLDER
from models import Movie

# Import các module của thành viên nhóm (Giữ nguyên đường dẫn import của bạn)
from movie_recommender_ai_module.data_processor import load_data
from movie_recommender_ai_module.recommender import ContentBasedRecommender
from booking_and_voice_search.booking_serveice import load_booking_data

def create_demo_image_file():
    """Tự động tạo file movie_images.csv nếu chưa có."""
    if not os.path.exists(FILE_IMAGES):
        # (Để ngắn gọn, tôi không paste lại chuỗi csv dài, bạn copy từ file cũ sang nhé)
        pass

def _create_movie_from_row(row):
    """Helper chuyển đổi dòng Dataframe thành Object Movie"""
    img_link = POSTER_PLACEHOLDER
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
    create_demo_image_file() # Đảm bảo file ảnh tồn tại
    df_movies = load_data()
    recommender = None
    movies_list_ui = []

    if not df_movies.empty:
        # Logic merge ảnh
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

        # Lấy 50 phim đầu tiên cho UI
        for index, row in df_movies.head(50).iterrows():
            movies_list_ui.append(_create_movie_from_row(row))

    if not movies_list_ui:
        movies_list_ui = [Movie(1, "Phim Demo", "Hành động", "120p", "C18", POSTER_PLACEHOLDER, 100000)]

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
        # Fallback tìm trong full data
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