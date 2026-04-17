from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(get_settings().embedding_model_name)


def embed_query(query: str) -> list[float]:
    cleaned_query = query.strip()
    if not cleaned_query:
        raise ValueError("Query must not be empty.")

    vector = get_embedding_model().encode(cleaned_query, convert_to_numpy=True, show_progress_bar=False)
    return [float(value) for value in vector.tolist()]
