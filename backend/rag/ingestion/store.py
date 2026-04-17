from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection

from rag.ingestion.config import get_config


def get_collection() -> Collection:
    config = get_config()
    if not config.mongodb_uri:
        raise RuntimeError("MONGODB_URI is not set in the environment.")

    client = MongoClient(
        config.mongodb_uri,
        appname="company-knowledge-ingestion",
        serverSelectionTimeoutMS=5000,
    )
    collection = client[config.database_name][config.collection_name]
    collection.create_index("metadata.chunk_id", unique=True)
    collection.create_index("metadata.source")
    return collection


def existing_sources(collection: Collection, sources: Iterable[str]) -> set[str]:
    source_list = sorted(set(source for source in sources if source))
    if not source_list:
        return set()

    return set(collection.distinct("metadata.source", {"metadata.source": {"$in": source_list}}))


def filter_duplicates(collection: Collection, records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], set[str]]:
    duplicates = existing_sources(collection, (record["metadata"]["source"] for record in records))
    if not duplicates:
        return records, set()

    filtered = [record for record in records if record["metadata"]["source"] not in duplicates]
    return filtered, duplicates


def insert_batches(collection: Collection, records: list[dict[str, Any]], batch_size: int) -> int:
    if not records:
        return 0

    inserted = 0
    for start in range(0, len(records), batch_size):
        batch = records[start : start + batch_size]
        result = collection.insert_many(batch, ordered=False)
        inserted += len(result.inserted_ids)
    return inserted
