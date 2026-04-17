from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import logging
import math
import re
from time import perf_counter
from typing import Any

from rag.retrieval.embedder import get_embedding_model
from rag.retrieval.vector_search import search_similar_chunks

logger = logging.getLogger(__name__)

_SYNONYM_EXPANSIONS = {
    "joining kit": "onboarding welcome kit",
    "welcome kit": "onboarding welcome kit",
    "join": "joining onboarding",
    "joining": "joining onboarding",
    "leave": "leave policy employee leave",
    "pto": "leave policy paid time off employee leave",
    "vacation": "leave policy vacation employee leave",
    "benefits": "employee benefits hr benefits",
    "deployment": "deployment process production release",
    "release": "deployment process production release",
    "incident": "incident response incident management",
    "escalation": "incident escalation matrix escalation path",
    "code standards": "engineering code standards",
    "account setup": "onboarding account setup",
}

_META_PATTERNS = (
    "can you answer",
    "what can you answer",
    "what can you do",
    "who are you",
    "how do you work",
    "what documents do you use",
    "what docs do you use",
    "are you able",
)

_FAQ_PATTERNS = (
    "how to",
    "how do i",
    "how can i",
    "where can i",
    "where do i",
    "who should i contact",
    "join",
    "joining",
    "welcome kit",
    "account setup",
)

_KNOWLEDGE_KEYWORDS = {
    "api",
    "backup",
    "benefits",
    "code",
    "conduct",
    "deployment",
    "engineering",
    "escalation",
    "guideline",
    "hr",
    "incident",
    "leave",
    "matrix",
    "onboarding",
    "operations",
    "policy",
    "procedure",
    "process",
    "response",
    "sop",
    "standard",
}


@dataclass(frozen=True)
class QueryAnalysis:
    original_query: str
    normalized_query: str
    expanded_query: str
    keyword_terms: list[str]
    query_terms: set[str]
    query_phrases: list[str]


@dataclass(frozen=True)
class RetrievalResult:
    chunks: list[dict[str, Any]]
    query_type: str
    normalized_query: str
    embedding_time_s: float
    retrieval_time_s: float
    rerank_time_s: float
    top_score: float | None
    confidence_band: str


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split()).strip()


def classify_query(query: str) -> str:
    lowered = _normalize_whitespace(query.lower())
    if not lowered:
        return "unknown"

    if any(pattern in lowered for pattern in _META_PATTERNS):
        return "meta"

    if any(pattern in lowered for pattern in _FAQ_PATTERNS):
        return "faq"

    if any(keyword in lowered for keyword in _KNOWLEDGE_KEYWORDS):
        return "knowledge"

    if lowered.endswith("?") and any(token in lowered for token in ("how", "where", "who")):
        return "faq"

    return "unknown"


def normalize_query(query: str) -> QueryAnalysis:
    lowered = query.lower().strip()
    sanitized = re.sub(r"[^a-z0-9\s]", " ", lowered)
    normalized = _normalize_whitespace(sanitized)

    expansions: list[str] = []
    for source, expansion in _SYNONYM_EXPANSIONS.items():
        if source in normalized:
            expansions.append(expansion)

    expanded_parts = [normalized, *expansions]
    expanded_query = _normalize_whitespace(" ".join(part for part in expanded_parts if part))
    raw_tokens = _tokenize(expanded_query)
    keyword_terms = [token for token, _ in Counter(raw_tokens).most_common() if len(token) > 2][:8]
    query_terms = set(keyword_terms)

    phrases: list[str] = []
    normalized_words = [word for word in normalized.split() if len(word) > 2]
    if len(normalized_words) >= 2:
        phrases.append(" ".join(normalized_words[:2]))
    if len(normalized_words) >= 3:
        phrases.append(" ".join(normalized_words[:3]))

    return QueryAnalysis(
        original_query=query.strip(),
        normalized_query=normalized,
        expanded_query=expanded_query,
        keyword_terms=keyword_terms,
        query_terms=query_terms,
        query_phrases=phrases,
    )


def _embed_query_batch(analysis: QueryAnalysis) -> list[float]:
    variants = [analysis.normalized_query]
    if analysis.expanded_query and analysis.expanded_query != analysis.normalized_query:
        variants.append(analysis.expanded_query)
    if analysis.original_query and analysis.original_query.lower() not in {variant.lower() for variant in variants}:
        variants.insert(0, analysis.original_query)

    model = get_embedding_model()
    vectors = model.encode(variants, convert_to_numpy=True, show_progress_bar=False)
    dimensions = len(vectors[0])
    averaged = [0.0] * dimensions

    for vector in vectors:
        for index, value in enumerate(vector.tolist()):
            averaged[index] += float(value)

    return [value / len(vectors) for value in averaged]


def _cosine_similarity(vector_a: list[float], vector_b: list[float] | None) -> float:
    if not vector_b or len(vector_a) != len(vector_b):
        return 0.0

    dot_product = sum(left * right for left, right in zip(vector_a, vector_b, strict=True))
    norm_a = math.sqrt(sum(value * value for value in vector_a))
    norm_b = math.sqrt(sum(value * value for value in vector_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return max(0.0, min(dot_product / (norm_a * norm_b), 1.0))


def _keyword_overlap_score(analysis: QueryAnalysis, content: str) -> float:
    content_terms = set(_tokenize(content))
    if not analysis.query_terms:
        return 0.0
    return len(content_terms & analysis.query_terms) / len(analysis.query_terms)


def _query_term_match_score(analysis: QueryAnalysis, content: str) -> float:
    normalized_content = _normalize_whitespace(content.lower())
    if not normalized_content:
        return 0.0

    matched_terms = sum(1 for term in analysis.query_terms if re.search(rf"\b{re.escape(term)}\b", normalized_content))
    term_score = matched_terms / max(len(analysis.query_terms), 1)
    phrase_matches = sum(1 for phrase in analysis.query_phrases if phrase and phrase in normalized_content)
    phrase_score = phrase_matches / max(len(analysis.query_phrases), 1) if analysis.query_phrases else 0.0
    return min(1.0, (term_score * 0.8) + (phrase_score * 0.2))


def _make_chunk_key(chunk: dict[str, Any]) -> tuple[str | None, Any, str | None]:
    metadata = chunk.get("metadata", {})
    return (
        metadata.get("source"),
        metadata.get("page"),
        metadata.get("chunk_id") or metadata.get("content_hash"),
    )


def _merge_hybrid_results(
    vector_results: list[dict[str, Any]],
    keyword_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged: dict[tuple[str | None, Any, str | None], dict[str, Any]] = {}

    for candidate in vector_results:
        chunk = dict(candidate)
        chunk["vector_score"] = float(chunk.get("vector_score", chunk.get("score", 0.0)) or 0.0)
        chunk["keyword_score"] = 0.0
        chunk["hybrid_score"] = 0.7 * chunk["vector_score"]
        merged[_make_chunk_key(chunk)] = chunk

    for candidate in keyword_results:
        key = _make_chunk_key(candidate)
        chunk = merged.get(key, dict(candidate))
        chunk["vector_score"] = float(chunk.get("vector_score", 0.0) or 0.0)
        chunk["keyword_score"] = float(candidate.get("keyword_score", candidate.get("score", 0.0)) or 0.0)
        if "content" not in chunk:
            chunk["content"] = candidate.get("content", "")
        if "metadata" not in chunk:
            chunk["metadata"] = candidate.get("metadata", {})
        if "embedding" not in chunk and candidate.get("embedding") is not None:
            chunk["embedding"] = candidate.get("embedding")
        chunk["hybrid_score"] = (0.7 * chunk["vector_score"]) + (0.3 * chunk["keyword_score"])
        merged[key] = chunk

    return sorted(merged.values(), key=lambda item: item.get("hybrid_score", 0.0), reverse=True)


def _is_relevant_chunk(chunk: dict[str, Any], analysis: QueryAnalysis, query_embedding: list[float]) -> bool:
    content = chunk.get("content", "").strip()
    if len(content) < 50:
        return False

    semantic_score = _cosine_similarity(query_embedding, chunk.get("embedding"))
    overlap_score = _keyword_overlap_score(analysis, content)
    return semantic_score >= 0.35 or overlap_score >= 0.2


def _optimize_context(
    candidates: list[dict[str, Any]],
    *,
    max_chunks: int,
) -> list[dict[str, Any]]:
    optimized: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()

    for candidate in candidates:
        metadata = candidate.get("metadata", {})
        content_hash = metadata.get("content_hash")
        if content_hash and content_hash in seen_hashes:
            continue
        if content_hash:
            seen_hashes.add(content_hash)

        candidate_tokens = set(_tokenize(candidate.get("content", "")))
        is_redundant = False
        for existing in optimized:
            existing_tokens = set(_tokenize(existing.get("content", "")))
            union = candidate_tokens | existing_tokens
            overlap = len(candidate_tokens & existing_tokens) / len(union) if union else 0.0
            same_source = metadata.get("source") == existing.get("metadata", {}).get("source")
            if overlap >= 0.82 or (same_source and overlap >= 0.7):
                if candidate.get("rerank_score", 0.0) > existing.get("rerank_score", 0.0):
                    existing["content"] = candidate.get("content", "")
                    existing["metadata"] = metadata
                    existing["score"] = candidate.get("score", existing.get("score"))
                    existing["vector_score"] = candidate.get("vector_score", existing.get("vector_score", 0.0))
                    existing["keyword_score"] = candidate.get("keyword_score", existing.get("keyword_score", 0.0))
                    existing["hybrid_score"] = candidate.get("hybrid_score", existing.get("hybrid_score", 0.0))
                    existing["rerank_score"] = candidate.get("rerank_score", existing.get("rerank_score", 0.0))
                is_redundant = True
                break

        if is_redundant:
            continue

        optimized.append(candidate)
        if len(optimized) >= max_chunks:
            break

    return optimized


def _rerank_chunks(
    candidates: list[dict[str, Any]],
    analysis: QueryAnalysis,
    query_embedding: list[float],
) -> list[dict[str, Any]]:
    reranked: list[dict[str, Any]] = []

    for candidate in candidates:
        content = candidate.get("content", "")
        cosine_score = _cosine_similarity(query_embedding, candidate.get("embedding"))
        overlap_score = _keyword_overlap_score(analysis, content)
        term_match_score = _query_term_match_score(analysis, content)

        reranked_candidate = dict(candidate)
        reranked_candidate["score"] = candidate.get("hybrid_score", 0.0)
        reranked_candidate["semantic_score"] = cosine_score
        reranked_candidate["keyword_overlap_score"] = overlap_score
        reranked_candidate["term_match_score"] = term_match_score
        reranked_candidate["rerank_score"] = (
            (0.5 * cosine_score) + (0.3 * overlap_score) + (0.2 * term_match_score)
        )
        reranked.append(reranked_candidate)

    reranked.sort(key=lambda chunk: chunk.get("rerank_score", 0.0), reverse=True)
    return reranked


def _confidence_band(score: float | None) -> str:
    if score is None:
        return "low"
    return "confident"


def retrieve_chunks(
    query: str,
    *,
    query_type: str | None = None,
    department: str | None = None,
    top_k: int = 5,
) -> RetrievalResult:
    normalized_department = department.strip() if department else None
    analysis = normalize_query(query)
    detected_query_type = query_type or classify_query(query)

    embedding_started_at = perf_counter()
    query_embedding = _embed_query_batch(analysis)
    embedding_time_s = perf_counter() - embedding_started_at

    retrieval_started_at = perf_counter()
    chunks = search_similar_chunks(
        query_embedding,
        department=normalized_department,
        top_k=top_k,
        score_threshold=None,
    )
    retrieval_time_s = perf_counter() - retrieval_started_at

    rerank_time_s = 0.0
    top_score = chunks[0].get("score") if chunks else None
    confidence_band = _confidence_band(top_score)

    logger.info(
        "retrieval_summary query_type=%s department=%s normalized_query=%r sources=%s confidence=%s",
        detected_query_type,
        normalized_department,
        analysis.expanded_query or analysis.normalized_query,
        [chunk.get("metadata", {}).get("source") for chunk in chunks],
        confidence_band,
    )

    logger.info(
        "retrieved %s raw vector chunks for query=%r with department=%s",
        len(chunks),
        query,
        normalized_department,
    )

    return RetrievalResult(
        chunks=chunks,
        query_type=detected_query_type,
        normalized_query=analysis.expanded_query or analysis.normalized_query,
        embedding_time_s=embedding_time_s,
        retrieval_time_s=retrieval_time_s,
        rerank_time_s=rerank_time_s,
        top_score=top_score,
        confidence_band=confidence_band,
    )


def get_relevant_chunks(
    query: str,
    *,
    query_type: str | None = None,
    department: str | None = None,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    return retrieve_chunks(
        query,
        query_type=query_type,
        department=department,
        top_k=top_k,
    ).chunks
