from pymongo.collection import Collection
from pymongo.results import InsertManyResult

from app.db.mongo import get_documents_collection


def get_document_collection() -> Collection:
    return get_documents_collection()


def insert_embedded_documents(texts: list[str], embeddings: list[list[float]]) -> InsertManyResult:
    if len(texts) != len(embeddings):
        raise ValueError("texts and embeddings must have the same length")

    if not texts:
        raise ValueError("No documents to store")

    payload = [
        {
            "text": text,
            "embedding": embedding,
        }
        for text, embedding in zip(texts, embeddings, strict=True)
    ]
    return get_document_collection().insert_many(payload)
