from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any
from uuid import uuid4


ChunkRecord = dict[str, Any]


def _normalize_chunk_text(text: str) -> str:
    return " ".join(text.split()).strip()


def _windowed_chunks(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    normalized = _normalize_chunk_text(text)
    if not normalized:
        return []

    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    start = 0
    step = max(chunk_size - chunk_overlap, 1)

    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            split_at = normalized.rfind(" ", start, end)
            if split_at > start + (chunk_size // 2):
                end = split_at

        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(normalized):
            break

        start = max(end - chunk_overlap, start + step)

    return chunks


def chunk_documents(
    documents: list[dict[str, Any]],
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> list[ChunkRecord]:
    chunks: list[ChunkRecord] = []

    for document in documents:
        content = document["content"]
        metadata = document["metadata"]
        for index, chunk_text in enumerate(_windowed_chunks(content, chunk_size, chunk_overlap), start=1):
            chunk_metadata = deepcopy(metadata)
            chunk_metadata["chunk_id"] = str(uuid4())
            chunk_metadata["chunk_index"] = index
            chunk_metadata["content_hash"] = sha256(chunk_text.encode("utf-8")).hexdigest()
            chunks.append({"content": chunk_text, "metadata": chunk_metadata})

    return chunks
