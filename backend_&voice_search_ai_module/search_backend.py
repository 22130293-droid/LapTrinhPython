import pandas as pd
from pathlib import Path
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np

class TFIDFMovieSearch:
    def __init__(self, movies_csv: str, text_fields: List[str] = None):
     
        self.movies_csv = Path(movies_csv)
        if not self.movies_csv.exists():
            raise FileNotFoundError(f"{movies_csv} not found")
        self.df = pd.read_csv(self.movies_csv)
        if text_fields is None:
            possible = ["title", "genres"]
            text_fields = [c for c in possible if c in self.df.columns]
            if len(text_fields) == 0:
                text_fields = [c for c in self.df.columns if self.df[c].dtype == "object"]
        self.text_fields = text_fields
        self._build_index()

    def _build_index(self):
        docs = self.df[self.text_fields].fillna("").agg(" ".join, axis=1)
        self.docs = docs.tolist()
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=20000)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.docs)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Trả về list (index_in_df, score)
        """
        if not isinstance(query, str) or query.strip() == "":
            return []
        q_vec = self.vectorizer.transform([query])
        cosine_similarities = linear_kernel(q_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(-cosine_similarities)[:top_k]
        results = [(int(i), float(cosine_similarities[i])) for i in top_indices if cosine_similarities[i] > 0]
        return results

    def get_movie_info(self, idx: int) -> dict:
        row = self.df.iloc[idx]
        return row.to_dict()
