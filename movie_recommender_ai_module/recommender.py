# File: movie_pyProject/ai_module/recommender.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# import os # Không cần thiết nữa
# Tải hàm load_data từ file data_processor.py
from .data_processor import load_data, DATA_FILE # .data_processor vì cùng package


class ContentBasedRecommender:
    # ... (các hàm __init__, _train_model, get_recommendations giữ nguyên) ...
    pass


if __name__ == "__main__":
    # --- PHẦN CHẠY THỬ NGHIỆM KHI CHẠY TRỰC TIẾP ---

    # 1. Tải dữ liệu (Gọi hàm đã được import)
    movies_df = load_data(DATA_FILE)

    # 2. Khởi tạo và huấn luyện recommender
    recommender = ContentBasedRecommender(movies_df)

    # 3. Chạy thử nghiệm
    # ... (phần còn lại giữ nguyên) ...