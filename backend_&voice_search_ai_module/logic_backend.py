# backend/recommender_oop.py
import os
import joblib
from typing import List, Dict, Any, Optional

class BaseRecommender:
    """Interface cơ bản cho recommender."""
    def recommend_by_movie(self, title: str, top_n: int = 10) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def recommend_by_user(self, user_id: int, top_n: int = 10) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def save(self, path: str):
        raise NotImplementedError

    def load(self, path: str):
        raise NotImplementedError


class UnifiedRecommender(BaseRecommender):
    """
    Kết hợp Content-based (TF-IDF) và Collaborative (SVD).
    Lưu/Load model bằng joblib.
    """

    def __init__(self, content_model=None, collab_model=None, movies_df=None):
        """
        content_model: instance giống ContentBasedRecommender
        collab_model: instance giống CollaborativeRecommender
        movies_df: DataFrame ban đầu (cần cho tìm title -> id)
        """
        self.content_model = content_model
        self.collab_model = collab_model
        self.movies_df = movies_df

    # --- Content based wrapper ---
    def recommend_by_movie(self, title: str, top_n: int = 10):
        if self.content_model is None:
            return []
        return self.content_model.recommend(title, top_n)

    # --- Collaborative wrapper ---
    def recommend_by_user(self, user_id: int, top_n: int = 10):
        if self.collab_model is None:
            return []
        recs = self.collab_model.recommend(user_id, top_n)
        # Nếu có movies_df, thêm title vào kết quả (nếu cần)
        if self.movies_df is not None and len(recs) > 0:
            id2title = dict(zip(self.movies_df["movieId"].astype(int), self.movies_df["title"]))
            for r in recs:
                r["title"] = id2title.get(int(r["movieId"]), None)
        return recs

    # --- Hỗ trợ lưu / load ---
    def save(self, path: str):
        os.makedirs(path, exist_ok=True)
        if self.content_model is not None:
            joblib.dump(self.content_model, os.path.join(path, "content_model.joblib"))
        if self.collab_model is not None:
            joblib.dump(self.collab_model, os.path.join(path, "collab_model.joblib"))
        # movies_df không lưu ở đây (có thể lưu riêng nếu cần)

    def load(self, path: str):
        content_path = os.path.join(path, "content_model.joblib")
        collab_path = os.path.join(path, "collab_model.joblib")
        if os.path.exists(content_path):
            self.content_model = joblib.load(content_path)
        if os.path.exists(collab_path):
            self.collab_model = joblib.load(collab_path)
