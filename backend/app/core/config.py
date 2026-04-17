import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings(BaseModel):
    app_name: str = "Company Knowledge Assistant"
    mongodb_uri: str = Field(default="", alias="MONGODB_URI")
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    mongo_database_name: str = "company_knowledge"
    mongo_collection_name: str = "rag_chunks"
    embedding_model_name: str = Field(default="all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    groq_model_name: str = "llama-3.1-8b-instant"
    vector_search_index_name: str = "vector_index"
    vector_search_embedding_path: str = "embedding"
    vector_search_dimensions: int = 384
    vector_search_top_k: int = 5
    vector_search_num_candidates: int = 50
    vector_search_score_threshold: float | None = None
    vector_search_required_filter_paths: tuple[str, ...] = (
        "metadata.department",
        "metadata.source",
        "metadata.page",
        "metadata.chunk_id",
    )
    chunk_size: int = 500
    chunk_overlap: int = 50


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    raw_score_threshold = os.getenv("VECTOR_SEARCH_SCORE_THRESHOLD", "").strip()
    score_threshold = float(raw_score_threshold) if raw_score_threshold else None
    raw_filter_paths = os.getenv(
        "VECTOR_SEARCH_REQUIRED_FILTER_PATHS",
        "metadata.department,metadata.source,metadata.page,metadata.chunk_id",
    )
    required_filter_paths = tuple(
        path.strip()
        for path in raw_filter_paths.split(",")
        if path.strip()
    )
    return Settings(
        MONGODB_URI=os.getenv("MONGODB_URI", ""),
        GROQ_API_KEY=os.getenv("GROQ_API_KEY", ""),
        EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        mongo_database_name=os.getenv("MONGO_DATABASE_NAME", "company_knowledge"),
        mongo_collection_name=os.getenv("MONGO_COLLECTION_NAME", "rag_chunks"),
        groq_model_name=os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant"),
        vector_search_index_name=os.getenv("VECTOR_SEARCH_INDEX_NAME", "vector_index"),
        vector_search_embedding_path=os.getenv("VECTOR_SEARCH_EMBEDDING_PATH", "embedding"),
        vector_search_dimensions=int(os.getenv("VECTOR_SEARCH_DIMENSIONS", "384")),
        vector_search_top_k=int(os.getenv("VECTOR_SEARCH_TOP_K", "5")),
        vector_search_num_candidates=int(os.getenv("VECTOR_SEARCH_NUM_CANDIDATES", "50")),
        vector_search_score_threshold=score_threshold,
        vector_search_required_filter_paths=required_filter_paths,
    )
