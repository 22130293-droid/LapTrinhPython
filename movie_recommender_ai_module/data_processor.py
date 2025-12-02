import pandas as pd
import os
import numpy as np

# --- CẤU HÌNH ĐƯỜNG DẪN DỮ LIỆU ---
# Giả định script được chạy từ thư mục gốc của dự án
DATA_DIR = 'data'

# Đường dẫn các file đầu vào
MOVIE_FILE = os.path.join(DATA_DIR, 'movies.csv')
RATING_FILE = os.path.join(DATA_DIR, 'ratings.csv')
TAGS_FILE = os.path.join(DATA_DIR, 'tags.csv')

# Đường dẫn file đầu ra (Cache)
CLEANED_FILE = os.path.join(DATA_DIR, 'cleaned_data.csv')

# Biến này để đảm bảo tương thích khi recommender.py import DATA_FILE
DATA_FILE = MOVIE_FILE


def process_and_merge_data(movie_path, rating_path, tags_path):
    """
    Hàm nội bộ: Thực hiện đọc file gốc, làm sạch và nối dữ liệu.
    Chỉ chạy khi chưa có file cleaned_data.csv.
    """
    print("🔄 Đang xử lý dữ liệu gốc (Merge Movies + Ratings + Tags)...")

    # 1. Đọc dữ liệu gốc
    try:
        df_movies = pd.read_csv(movie_path)
        df_ratings = pd.read_csv(rating_path)
        df_tags = pd.read_csv(tags_path)
    except FileNotFoundError as e:
        print(f"❌ Lỗi: Không tìm thấy file dữ liệu gốc: {e}")
        print(f"👉 Vui lòng kiểm tra thư mục '{DATA_DIR}/' đã có đủ movies.csv, ratings.csv, tags.csv chưa.")
        return pd.DataFrame()

    # 2. Xử lý Ratings (Tính điểm trung bình và số lượng đánh giá)
    # Gom nhóm theo movieId, tính trung bình rating và đếm số lượng
    rating_stats = df_ratings.groupby('movieId')['rating'].agg(['mean', 'count']).reset_index()
    rating_stats.columns = ['movieId', 'average_rating', 'rating_count']

    # Nối vào bảng movies
    df_merged = pd.merge(df_movies, rating_stats, on='movieId', how='left')

    # Xử lý giá trị thiếu (NaN) cho phim chưa có đánh giá nào
    df_merged['average_rating'] = df_merged['average_rating'].fillna(0)
    df_merged['rating_count'] = df_merged['rating_count'].fillna(0).astype(int)

    # 3. Xử lý Tags (Gộp tất cả tags của một phim thành 1 chuỗi)
    # Chuyển tag sang string đề phòng lỗi, sau đó join lại bằng dấu cách
    tags_grouped = df_tags.groupby('movieId')['tag'].apply(lambda x: ' '.join(x.astype(str))).reset_index()
    tags_grouped.columns = ['movieId', 'tags_combined']

    # Nối vào bảng movies
    df_merged = pd.merge(df_merged, tags_grouped, on='movieId', how='left')
    df_merged['tags_combined'] = df_merged['tags_combined'].fillna('')

    # 4. Tiền xử lý văn bản cho Content-Based (Cột Genres)
    # Thay thế ký tự '|' bằng khoảng trắng để TF-IDF vectorizer hiểu
    df_merged['genres'] = df_merged['genres'].fillna('')
    df_merged['genres_clean'] = df_merged['genres'].str.replace('|', ' ', regex=False)

    return df_merged


def load_all_data(cleaned_path=CLEANED_FILE):
    """
    Hàm chính: Tải dữ liệu đầy đủ.
    Ưu tiên đọc từ file đã xử lý (cleaned_data.csv) để tăng tốc độ.
    Nếu chưa có, gọi hàm xử lý và lưu lại file mới.
    """

    # --- BƯỚC 1: KIỂM TRA CACHE ---
    if os.path.exists(cleaned_path):
        print(f"✅ Tìm thấy file dữ liệu đã xử lý: {cleaned_path}")
        try:
            df = pd.read_csv(cleaned_path)
            # Kiểm tra nhanh xem file có đủ cột không, nếu lỗi thì xử lý lại
            if 'average_rating' in df.columns and 'genres_clean' in df.columns:
                return df
            else:
                print("⚠️ File đã xử lý thiếu cột cần thiết. Đang xử lý lại...")
        except Exception as e:
            print(f"⚠️ Lỗi khi đọc file cache: {e}. Đang xử lý lại...")

    # --- BƯỚC 2: XỬ LÝ NẾU CHƯA CÓ CACHE HOẶC LỖI ---
    df_final = process_and_merge_data(MOVIE_FILE, RATING_FILE, TAGS_FILE)

    if not df_final.empty:
        # --- BƯỚC 3: LƯU FILE CACHE ---
        try:
            df_final.to_csv(cleaned_path, index=False)
            print(f"💾 Đã lưu dữ liệu sau xử lý vào: {cleaned_path}")
        except Exception as e:
            print(f"⚠️ Không thể lưu file cleaned_data.csv: {e}")

    return df_final


def load_data(file_path=None):
    """
    Wrapper function: Giữ hàm này để tương thích ngược với recommender.py cũ.
    Dù tham số file_path có là gì, ta vẫn ưu tiên gọi load_all_data().
    """
    return load_all_data()


# --- PHẦN CHẠY THỬ NGHIỆM (Khi chạy trực tiếp file này) ---
if __name__ == "__main__":
    print("--- TEST MODULE DATA PROCESSOR ---")

    # Test: Load dữ liệu
    df = load_all_data()

    if not df.empty:
        print(f"\n✅ Tải thành công {len(df)} bộ phim.")
        print("\n--- 5 Dòng đầu tiên (Kiểm tra các cột mới) ---")
        print(df[['title', 'genres_clean', 'average_rating', 'rating_count', 'tags_combined']].head())

        # Test: Tìm phim nổi tiếng nhất
        print("\n--- Phim có nhiều lượt đánh giá nhất ---")
        top_movie = df.sort_values(by='rating_count', ascending=False).iloc[0]
        print(f"Phim: {top_movie['title']}")
        print(f"Rating TB: {top_movie['average_rating']:.1f}/5.0 ({top_movie['rating_count']} lượt)")
        print(f"Tags: {top_movie['tags_combined'][:100]}...")
    else:
        print("❌ Không tải được dữ liệu.")