from __future__ import annotations

import logging
import sys
from pathlib import Path


if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from rag.ingestion.chunker import chunk_documents
from rag.ingestion.config import get_config
from rag.ingestion.embedder import embed_chunks
from rag.ingestion.loader import load_all_documents
from rag.ingestion.store import filter_duplicates, get_collection, insert_batches


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("rag.ingestion.pipeline")


def run_pipeline() -> dict[str, int]:
    config = get_config()

    logger.info("Loading source documents from %s", config.data_root)
    documents = load_all_documents(config.data_root)
    logger.info("Loaded %s source documents", len(documents))

    logger.info(
        "Creating chunks with chunk_size=%s and chunk_overlap=%s",
        config.chunk_size,
        config.chunk_overlap,
    )
    chunks = chunk_documents(
        documents,
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
    )
    logger.info("Created %s chunks", len(chunks))

    logger.info("Generating embeddings with model %s", config.embedding_model)
    embedded_chunks = embed_chunks(chunks, batch_size=config.embedding_batch_size)

    logger.info(
        "Connecting to MongoDB database=%s collection=%s",
        config.database_name,
        config.collection_name,
    )
    collection = get_collection()

    chunks_to_insert, duplicate_sources = filter_duplicates(collection, embedded_chunks)
    if duplicate_sources:
        logger.info("Skipping %s already-ingested sources: %s", len(duplicate_sources), ", ".join(sorted(duplicate_sources)))

    inserted_count = insert_batches(collection, chunks_to_insert, batch_size=config.insert_batch_size)
    logger.info("Inserted %s chunks into MongoDB", inserted_count)

    return {
        "documents_processed": len(documents),
        "chunks_created": len(chunks),
        "chunks_inserted": inserted_count,
        "sources_skipped": len(duplicate_sources),
    }


def main() -> None:
    try:
        summary = run_pipeline()
    except Exception:
        logger.exception("Ingestion pipeline failed")
        raise

    print("Ingestion complete")
    print(f"Documents processed: {summary['documents_processed']}")
    print(f"Chunks created: {summary['chunks_created']}")
    print(f"Chunks inserted: {summary['chunks_inserted']}")
    print(f"Sources skipped: {summary['sources_skipped']}")


if __name__ == "__main__":
    main()
