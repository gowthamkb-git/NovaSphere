from __future__ import annotations

import logging
from typing import Any

from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from app.core.config import get_settings
from app.db.mongo import get_mongo_client

logger = logging.getLogger(__name__)


def _get_search_collection(collection: Collection | None = None) -> Collection:
    if collection is not None:
        return collection
    client = get_mongo_client()
    db = client["company_knowledge"]
    return db["rag_chunks"]


def validate_vector_search_index(collection: Collection | None = None) -> None:
    settings = get_settings()
    search_collection = _get_search_collection(collection)
    indexes = list(search_collection.list_search_indexes())

    if not indexes:
        raise RuntimeError(
            f"MongoDB Atlas Vector Search index '{settings.vector_search_index_name}' was not found."
        )

    index = next((item for item in indexes if item.get("name") == settings.vector_search_index_name), None)
    if index is None:
        available = ", ".join(sorted(item.get("name", "<unknown>") for item in indexes))
        raise RuntimeError(
            f"MongoDB Atlas Vector Search index '{settings.vector_search_index_name}' was not found. "
            f"Available indexes: {available or 'none'}."
        )

    if index.get("status") != "READY" or not index.get("queryable", False):
        raise RuntimeError(
            f"MongoDB Atlas Vector Search index '{settings.vector_search_index_name}' is not ready yet. "
            f"Current status: {index.get('status')}."
        )

    definition = index.get("latestDefinition") or index.get("definition") or {}
    fields = definition.get("fields", [])
    vector_field = next(
        (
            field
            for field in fields
            if field.get("type") == "vector" and field.get("path") == settings.vector_search_embedding_path
        ),
        None,
    )
    if vector_field is None:
        raise RuntimeError(
            f"MongoDB Atlas Vector Search index '{settings.vector_search_index_name}' is missing "
            f"the vector field '{settings.vector_search_embedding_path}'."
        )

    if int(vector_field.get("numDimensions", -1)) != settings.vector_search_dimensions:
        raise RuntimeError(
            f"MongoDB Atlas Vector Search index '{settings.vector_search_index_name}' has numDimensions="
            f"{vector_field.get('numDimensions')}, expected {settings.vector_search_dimensions}."
        )

    logger.info(
        "Validated Atlas Vector Search index '%s' on company_knowledge.rag_chunks",
        settings.vector_search_index_name,
    )


def search_similar_chunks(
    query_embedding: list[float],
    *,
    department: str | None = None,
    departments: tuple[str, ...] | None = None,
    top_k: int | None = None,
    score_threshold: float | None = None,
    include_embedding: bool = True,
    collection: Collection | None = None,
) -> list[dict[str, Any]]:
    del department, departments, score_threshold, include_embedding

    search_collection = _get_search_collection(collection)
    cleaned_query_embedding = [float(value) for value in query_embedding]
    limit = top_k or 5

    print("Embedding length:", len(cleaned_query_embedding))

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": cleaned_query_embedding,
                "numCandidates": 100,
                "limit": limit,
            }
        },
        {
            "$project": {
                "_id": 0,
                "content": 1,
                "metadata": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    logger.info("Running raw Atlas vector search on company_knowledge.rag_chunks")
    try:
        results = list(search_collection.aggregate(pipeline))
    except OperationFailure as exc:
        message = str(exc)
        if "needs to be indexed as filter" in message:
            raise RuntimeError(
                "MongoDB Atlas Vector Search index is missing a required filter field. "
                "Add the requested metadata path as type 'filter' in the vector index definition, "
                "or remove that filter from the query."
            ) from exc
        raise

    print("Mongo results count:", len(results))
    print(results[:1])

    if len(results) == 0:
        logger.warning("Vector search returned no results")

    chunks = [
        {
            "content": doc["content"],
            "metadata": doc["metadata"],
            "score": doc.get("score", 0),
        }
        for doc in results
    ]
    return chunks
