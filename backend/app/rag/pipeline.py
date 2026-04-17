"""Deprecated compatibility wrapper for ingestion utilities."""

from app.services.document_ingestion_service import (
    SEED_KNOWLEDGE_URL as INGESTION_URL,
    ingest_seed_knowledge as ingest_data,
)
