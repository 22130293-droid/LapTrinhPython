# File: movie_pyProject/ai_module/data_processor.py

import pandas as pd
import os

# Đường dẫn file dữ liệu
DATA_FILE = os.path.join('data', 'movies.csv')


def load_data(file_path=DATA_FILE):
    """Tải và tiền xử lý dữ liệu phim."""
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {file_path}. Đảm bảo đường dẫn đúng.")
        return pd.DataFrame()

    if not df.empty:
        # Tiền xử lý (Clean genres)
        df['genres_clean'] = df['genres'].str.replace('|', ' ')

        # MẸO: Thêm các bước tiền xử lý khác ở đây (ví dụ: xử lý NaN, nối tags, v.v.)
    return df