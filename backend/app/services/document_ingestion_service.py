import logging

from app.repositories.document_repository import insert_embedded_documents
from app.services.document_chunking_service import split_documents
from app.services.document_embedding_service import embed_texts
from app.services.web_content_service import load_web_documents

logger = logging.getLogger(__name__)

SEED_KNOWLEDGE_URL = "https://lilianweng.github.io/posts/2023-06-23-agent/"


def ingest_seed_knowledge() -> int:
    logger.info("Loading source documents from %s", SEED_KNOWLEDGE_URL)
    documents = load_web_documents(SEED_KNOWLEDGE_URL)

    logger.info("Splitting documents into chunks")
    chunks = split_documents(documents)
    texts = [chunk.page_content.strip() for chunk in chunks if chunk.page_content.strip()]

    if not texts:
        raise ValueError("No text chunks were generated from the source document.")

    logger.info("Generating embeddings for %s chunks", len(texts))
    embeddings = embed_texts(texts)

    logger.info("Storing embedded chunks in MongoDB")
    result = insert_embedded_documents(texts, embeddings)
    return len(result.inserted_ids)
