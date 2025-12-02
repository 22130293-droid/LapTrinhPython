import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# Đường dẫn file dữ liệu
DATA_FILE = os.path.join('data', 'movies.csv')


def load_data(file_path):
    """Tải và tiền xử lý dữ liệu phim."""
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {file_path}. Đảm bảo đường dẫn đúng.")
        return pd.DataFrame()

    if not df.empty:
        df['genres_clean'] = df['genres'].str.replace('|', ' ')
    return df


class ContentBasedRecommender:
    def __init__(self, df_movies):
        self.df_movies = df_movies
        self.cosine_sim = None
        self.indices = None

        if not self.df_movies.empty:
            self._train_model()

    def _train_model(self):
        """Huấn luyện model (Tính toán ma trận tương đồng)."""
        print("Đang huấn luyện AI (Tính toán sự giống nhau)...")

        # Vector hóa văn bản
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(self.df_movies['genres_clean'])

        # Tính ma trận tương đồng
        self.cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Tạo bảng tra cứu ngược
        self.indices = pd.Series(self.df_movies.index, index=self.df_movies['title']).drop_duplicates()

        print("✅ Training xong! Sẵn sàng gợi ý.")

    def get_recommendations(self, title, top_n=5):
        """Trả về danh sách các phim gợi ý dựa trên tên phim."""
        if self.df_movies.empty or self.cosine_sim is None:
            return ["Lỗi: Model chưa được huấn luyện do thiếu dữ liệu."]

        try:
            # Tìm index của phim (sử dụng tìm kiếm gần đúng/chứa)
            idx = self.indices[self.indices.index.str.contains(title, case=False)][0]
        except IndexError:
            return [f"Xin lỗi, không tìm thấy phim nào tên là '{title}'"]

        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n + 1]

        movie_indices = [i[0] for i in sim_scores]
        return self.df_movies['title'].iloc[movie_indices].tolist()


if __name__ == "__main__":
    # --- PHẦN CHẠY THỬ NGHIỆM KHI CHẠY TRỰC TIẾP ---

    # 1. Tải dữ liệu
    movies_df = load_data(DATA_FILE)

    # 2. Khởi tạo và huấn luyện recommender
    recommender = ContentBasedRecommender(movies_df)

    # 3. Chạy thử nghiệm
    if not movies_df.empty:
        test_title = 'Toy Story'  # Ví dụ
        recommendations = recommender.get_recommendations(test_title)

        print(f"\n--- Gợi ý 5 phim cho '{test_title}' ---")
        for i, rec in enumerate(recommendations):
            print(f"{i + 1}. {rec}")