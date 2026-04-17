from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from rag.ingestion.config import get_config


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(get_config().embedding_model)


def embed_chunks(chunks: list[dict], batch_size: int) -> list[dict]:
    if not chunks:
        return []

    model = get_embedding_model()
    texts = [chunk["content"] for chunk in chunks]
    vectors = model.encode(texts, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=False)

    embedded_chunks: list[dict] = []
    for chunk, vector in zip(chunks, vectors, strict=True):
        embedded_chunks.append(
            {
                "content": chunk["content"],
                "embedding": [float(value) for value in vector.tolist()],
                "metadata": chunk["metadata"],
            }
        )

    return embedded_chunks
