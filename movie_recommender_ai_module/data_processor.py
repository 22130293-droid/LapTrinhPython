# File: movie_pyProject/ai_module/data_processor.py

import pandas as pd
import os
import numpy as np

# Đường dẫn đến tất cả các file dữ liệu
DATA_DIR = 'data'
MOVIE_FILE = os.path.join(DATA_DIR, 'movies.csv')
RATING_FILE = os.path.join(DATA_DIR, 'ratings.csv')
TAGS_FILE = os.path.join(DATA_DIR, 'tags.csv')

# Đặt DATA_FILE gốc thành MOVIE_FILE để giữ nguyên tính tương thích
DATA_FILE = MOVIE_FILE


def load_all_data(movie_file=MOVIE_FILE, rating_file=RATING_FILE, tags_file=TAGS_FILE):
    """
    Tải, tiền xử lý và nối (merge) tất cả các file movies, ratings, tags.

    Trả về DataFrame df_movies đã được bổ sung cột rating trung bình và tags phổ biến.
    """

    # --- 1. Tải Dữ liệu Gốc ---
    try:
        df_movies = pd.read_csv(movie_file)
        df_ratings = pd.read_csv(rating_file)
        df_tags = pd.read_csv(tags_file)
    except FileNotFoundError as e:
        print(f"Lỗi: Không tìm thấy file dữ liệu: {e}. Đảm bảo các file ở thư mục '{DATA_DIR}/'")
        return pd.DataFrame()

    # --- 2. Tiền xử lý dữ liệu Movies (Content-Based) ---
    df_movies['genres'] = df_movies['genres'].fillna('')  # Xử lý NaN
    df_movies['genres_clean'] = df_movies['genres'].str.replace('|', ' ')

    # --- 3. Xử lý Ratings (Tính điểm trung bình) ---
    # Tính điểm trung bình và số lượng đánh giá cho mỗi phim
    rating_counts = df_ratings.groupby('movieId')['rating'].agg(['mean', 'count']).reset_index()
    rating_counts.columns = ['movieId', 'average_rating', 'rating_count']

    # Merge Ratings vào Movies
    df_movies = pd.merge(df_movies, rating_counts, on='movieId', how='left')
    df_movies['average_rating'] = df_movies['average_rating'].fillna(0)
    df_movies['rating_count'] = df_movies['rating_count'].fillna(0).astype(int)

    # --- 4. Xử lý Tags (Kết hợp các tags thành một chuỗi) ---
    # Gộp tất cả tags cho mỗi phim thành một chuỗi duy nhất
    df_tags_grouped = df_tags.groupby('movieId')['tag'].apply(lambda x: ' '.join(x.astype(str))).reset_index()
    df_tags_grouped.columns = ['movieId', 'tags_combined']

    # Merge Tags vào Movies
    df_movies = pd.merge(df_movies, df_tags_grouped, on='movieId', how='left')
    df_movies['tags_combined'] = df_movies['tags_combined'].fillna('')  # Xử lý NaN

    # --- 5. Tùy chọn: Ghi file Cleaned Data (data/cleaned_data.csv) ---
    # Điều này giúp các lần chạy sau nhanh hơn
    cleaned_file_path = os.path.join(DATA_DIR, 'cleaned_data.csv')
    df_movies.to_csv(cleaned_file_path, index=False)
    print(f"✅ Đã lưu dữ liệu đã tiền xử lý vào: {cleaned_file_path}")

    return df_movies


# Giữ nguyên hàm load_data gốc để đảm bảo tính tương thích với recommender.py
# Hàm này giờ sẽ gọi hàm load_all_data để có dữ liệu đầy đủ
def load_data(file_path=MOVIE_FILE):
    """Sử dụng hàm load_all_data để tải dữ liệu đầy đủ cho recommender."""
    return load_all_data()


# --- Phần chạy thử nghiệm (Optional) ---
if __name__ == "__main__":
    print("--- Bắt đầu kiểm tra data_processor (Load đầy đủ) ---")
    full_df = load_all_data()

    if not full_df.empty:
        print(f"\nTổng số phim đã xử lý: {len(full_df)}")
        print("\n--- Dữ liệu đã xử lý (5 dòng đầu) ---")
        print(full_df[['title', 'genres_clean', 'average_rating', 'tags_combined']].head())

        # Example check for a movie with high ratings/tags
        print("\nKiểm tra phim có nhiều đánh giá:")
        popular_movie = full_df.sort_values(by='rating_count', ascending=False).iloc[0]
        print(
            f"Phim: {popular_movie['title']} | Rating TB: {popular_movie['average_rating']:.2f} | Tags: {popular_movie['tags_combined'][:50]}...")