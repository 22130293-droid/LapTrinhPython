# File: movie_pyProject/ai_module/recommender.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re  # Cần thiết để xử lý các ký tự đặc biệt trong tên phim

# Tải hàm load_data và DATA_FILE từ file data_processor.py
# Dấu chấm (.) báo hiệu đây là relative import trong cùng một package
from .data_processor import load_data, DATA_FILE


class ContentBasedRecommender:
    """
    Hệ thống gợi ý phim Content-Based được cải tiến (Hybrid)
    Bao gồm reranking dựa trên chất lượng (Weighted Rating).
    """

    def __init__(self, df_movies):
        self.df_movies = df_movies
        self.cosine_sim = None
        self.indices = None
        self.C = 0  # Mean rating across all movies
        self.m = 0  # Minimum votes required (90th percentile)

        if not self.df_movies.empty:
            self._train_model()
            self._calculate_weighted_rank_params()

    def _calculate_weighted_rank_params(self):
        """Tính toán các tham số C (Điểm trung bình) và m (Số vote tối thiểu) cho Weighted Rating."""

        # C: Điểm đánh giá trung bình của TẤT CẢ các bộ phim
        self.C = self.df_movies['average_rating'].mean()

        # m: Số lượng đánh giá tối thiểu (lấy percentile 90 để loại bỏ phim ít vote)
        self.m = self.df_movies['rating_count'].quantile(0.90)

        print(f"Tham số Weighted Rank: C={self.C:.2f}, m={self.m:.0f} votes.")

    def _train_model(self):
        """
        Huấn luyện model: Sử dụng kết hợp Genres và Tags
        để tạo ra ma trận tương đồng Content-Based.
        """
        print("Đang huấn luyện AI (Content-Based) với Genres và Tags...")

        # Tạo cột tính năng bằng cách nối Genres và Tags
        self.df_movies['content_features'] = (
                self.df_movies['genres_clean'].fillna('') + ' ' +
                self.df_movies['tags_combined'].fillna('')
        )

        # Vector hóa văn bản
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(self.df_movies['content_features'])

        # Tính ma trận tương đồng (Cosine Similarity)
        self.cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Tạo bảng tra cứu ngược để tìm index từ tên phim
        self.indices = pd.Series(self.df_movies.index, index=self.df_movies['title']).drop_duplicates()

        print("✅ Training xong! Sẵn sàng gợi ý Hybrid.")

    def calculate_wr(self, df):
        """
        Tính toán Weighted Rating (WR) cho mỗi phim dựa trên công thức IMDb.
        WR = (v / (v + m) * R) + (m / (v + m) * C)
        """
        v = df['rating_count']
        R = df['average_rating']

        # Áp dụng công thức, sử dụng WR làm điểm xếp hạng chất lượng cuối cùng
        df['weighted_rating'] = np.where(
            v >= self.m,
            (v / (v + self.m) * R) + (self.m / (v + self.m) * self.C),
            R  # Giữ nguyên R (average_rating) nếu số vote quá ít (độ tin cậy thấp)
        )
        return df['weighted_rating']

    def get_recommendations(self, title, top_n=10):
        """Trả về danh sách các phim gợi ý, RERANKED theo chất lượng (WR)."""

        if self.df_movies.empty or self.cosine_sim is None:
            return [f"Lỗi: Model chưa được huấn luyện do thiếu dữ liệu."]

        # 1. Tìm index của phim (Đã FIX lỗi RegEx và tìm kiếm)
        try:
            # Escape ký tự đặc biệt trong tên phim để tránh lỗi RegEx (ví dụ: dấu ngoặc tròn)
            safe_title = re.escape(title)

            # Tìm kiếm tên phim và lấy index đầu tiên tìm được
            idx = self.indices[self.indices.index.str.contains(safe_title, case=False, regex=True)].iloc[0]
        except IndexError:
            return [f"Xin lỗi, không tìm thấy phim nào tên là '{title}'"]

        # 2. Lấy danh sách điểm tương đồng
        sim_scores = list(enumerate(self.cosine_sim[idx]))

        # 3. Sắp xếp theo điểm tương đồng cao nhất
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # 4. Lấy 50 phim TƯƠNG ĐỒNG NHẤT (trừ chính nó) để RERANK
        top_similar_indices = [i[0] for i in sim_scores[1:51]]

        # Tạo DataFrame tạm thời cho các phim tương đồng
        df_similar = self.df_movies.iloc[top_similar_indices].copy()

        # 5. Tính toán Weighted Rating (WR)
        df_similar['WR'] = self.calculate_wr(df_similar)

        # 6. RERANK: Sắp xếp lại danh sách dựa trên điểm Weighted Rating (WR)
        final_recommendations = df_similar.sort_values(by='WR', ascending=False)

        # Trả về top_n phim sau khi đã rerank
        return final_recommendations['title'].head(top_n).tolist()


if __name__ == "__main__":
    # --- PHẦN CHẠY THỬ NGHIỆM KHI CHẠY TRỰC TIẾP ---

    print("--- TEST MODULE RECOMMENDER (Hybrid) ---")

    # 1. Tải dữ liệu (Gọi hàm load_data đã được tối ưu hiệu suất)
    movies_df = load_data()

    # 2. Khởi tạo và huấn luyện recommender
    recommender = ContentBasedRecommender(movies_df)

    # 3. Chạy thử nghiệm
    if not movies_df.empty:
        # Sử dụng các phim đã gây lỗi trước đó để kiểm tra
        test_titles = ['Toy Story', 'Heat (1995)', 'Matrix, The (1999)', 'Iron Man']

        for title in test_titles:
            recommendations = recommender.get_recommendations(title, top_n=5)
            print(f"\n--- Gợi ý 5 phim Hybrid cho '{title}' (Genres + Tags + WR) ---")
            for i, rec in enumerate(recommendations):
                print(f"{i + 1}. {rec}")