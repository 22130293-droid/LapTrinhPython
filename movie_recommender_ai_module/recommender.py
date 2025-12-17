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
        print("Đang huấn luyện AI bản nâng cấp...")

        # CHIẾN THUẬT MỚI: Tăng trọng số cho Tiêu đề (nhân 3 lần) để bắt đúng series phim
        self.df_movies['content_features'] = (
                (self.df_movies['title'].fillna('') + ' ') * 3 +
                self.df_movies['genres_clean'].fillna('') + ' ' +
                self.df_movies['tags_combined'].fillna('')
        )

        # Sử dụng ngram_range=(1, 2) để bắt được các cụm từ như "Toy Story" thay vì chỉ "Toy"
        tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = tfidf.fit_transform(self.df_movies['content_features'])

        self.cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        self.indices = pd.Series(self.df_movies.index, index=self.df_movies['title']).drop_duplicates()
        print("✅ Đã nâng cấp logic nhận diện thương hiệu phim!")

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
        """
        Hệ thống gợi ý Hybrid nâng cao:
        Content Similarity + Series Boosting + Genre Penalty/Bonus + Weighted Rating.
        """
        if self.df_movies.empty or self.cosine_sim is None:
            return [f"Lỗi: Model chưa được huấn luyện."]

        try:
            # 1. Tìm phim gốc (Input)
            safe_title = re.escape(title)
            match_df = self.df_movies[self.df_movies['title'].str.contains(safe_title, case=False, na=False)]

            if match_df.empty:
                return [f"Xin lỗi, không tìm thấy phim nào chứa từ khóa '{title}'"]

            idx = match_df.index[0]
            input_row = match_df.iloc[0]
            input_movie_full_title = input_row['title']
            # Lấy tập hợp các thể loại của phim gốc để so sánh
            input_genres = set(str(input_row['genres']).split('|'))

            # Lấy từ khóa chính của thương hiệu (ví dụ: "Transformers")
            main_keyword = title.split(':')[0].strip()
        except Exception as e:
            return [f"Lỗi hệ thống khi tìm kiếm: {str(e)}"]

        # 2. Lấy danh sách phim tương đồng nhất từ ma trận Cosine (Lấy 100 phim để Rerank)
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        top_indices = [i[0] for i in sim_scores[1:101]]
        df_similar = self.df_movies.iloc[top_indices].copy()

        # --- BẮT ĐẦU CÁC LỚP LỌC TỐI ƯU (RERANKING) ---

        # 3. SERIES BOOSTING (Ưu tiên tuyệt đối phim cùng bộ)
        # Nếu tiêu đề chứa từ khóa chính, cộng 50 điểm
        df_similar['series_score'] = df_similar['title'].str.contains(main_keyword, case=False).astype(int) * 50

        # 4. GENRE PENALTY & BONUS (Lọc theo thể loại)
        def calculate_genre_logic(row_genres):
            target_genres = set(str(row_genres).split('|'))
            common_count = len(input_genres.intersection(target_genres))

            # Nếu không trùng bất kỳ thể loại nào -> Phạt nặng (-20 điểm)
            if common_count == 0:
                return -20
            # Nếu trùng thể loại -> Cộng điểm thưởng (5 điểm mỗi thể loại trùng)
            return common_count * 5

        df_similar['genre_score'] = df_similar['genres'].apply(calculate_genre_logic)

        # 5. WEIGHTED RATING (WR) - Chất lượng phim thực tế
        df_similar['WR'] = self.calculate_wr(df_similar)

        # 6. TỔNG HỢP ĐIỂM CUỐI CÙNG
        # Kết quả = Điểm thương hiệu + Điểm thể loại + Điểm chất lượng (WR)
        df_similar['final_score'] = df_similar['series_score'] + df_similar['genre_score'] + df_similar['WR']

        # Sắp xếp giảm dần theo final_score
        final_recommendations = df_similar.sort_values(by='final_score', ascending=False)

        # Trả về kết quả (DataFrame)
        return final_recommendations.head(top_n)


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