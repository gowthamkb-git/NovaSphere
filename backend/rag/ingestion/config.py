from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


@dataclass(frozen=True)
class IngestionConfig:
    mongodb_uri: str
    embedding_model: str
    database_name: str = "company_knowledge"
    collection_name: str = "rag_chunks"
    chunk_size: int = 800
    chunk_overlap: int = 100
    embedding_batch_size: int = 32
    insert_batch_size: int = 100

    @property
    def data_root(self) -> Path:
        return Path(__file__).resolve().parents[3] / "data"


def get_config() -> IngestionConfig:
    return IngestionConfig(
        mongodb_uri=os.getenv("MONGODB_URI", "").strip(),
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2").strip() or "all-MiniLM-L6-v2",
    )
