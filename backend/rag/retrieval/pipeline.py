from __future__ import annotations

import logging
import re
from time import perf_counter
from typing import Any

from app.core.config import get_settings
from rag.retrieval.generator import generate_answer
from rag.retrieval.prompt_builder import build_prompt
from rag.retrieval.retriever import classify_query, retrieve_chunks

logger = logging.getLogger(__name__)

_IDK_RESPONSE = "I don't know"
_PARTIAL_LEADS = (
    "The exact detail is not specified.",
    "This is not explicitly mentioned.",
    "The documents do not define this clearly.",
)
_UNSUPPORTED_INFERENCE_PHRASES = (
    "it appears",
    "it seems",
    "likely",
    "probably",
    "typically",
    "generally",
    "usually",
    "approximately",
    "approximate",
    "around ",
    "about ",
    "private company",
    "public company",
    "financial",
    "revenue",
    "profit",
)
_VALIDATION_STOPWORDS = {
    "a",
    "about",
    "after",
    "all",
    "also",
    "an",
    "and",
    "answer",
    "available",
    "based",
    "be",
    "by",
    "can",
    "company",
    "context",
    "documents",
    "for",
    "from",
    "i",
    "in",
    "is",
    "it",
    "know",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "we",
    "with",
}


def _build_sources(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, Any]] = set()
    sources: list[dict[str, Any]] = []

    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        source = metadata.get("source")
        page = metadata.get("page")
        if not source:
            continue

        key = (source, page)
        if key in seen:
            continue

        seen.add(key)
        formatted_source = f"{source} (page {page})" if page is not None else source
        sources.append({"source": formatted_source, "page": page})

    return sources


def _log_chunk_previews(chunks: list[dict[str, Any]]) -> None:
    for index, chunk in enumerate(chunks[:2], start=1):
        preview = " ".join(chunk.get("content", "").split())[:200]
        logger.info("Top chunk %s preview: %s", index, preview)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _extract_sentences(text: str) -> list[str]:
    return [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", text.strip()) if segment.strip()]


def _sanitize_summary_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    cleaned = re.sub(r"^(chunk\s*\d+\s*\|.*?)(?=[A-Za-z0-9])", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bsource=[^|]+(?:\|\s*)?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bpage=\d+(?:\|\s*)?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bversion\s+\S+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\binternal\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" |:-")
    return cleaned


def _looks_incomplete(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if stripped.endswith((":", ";", ",", "|", "-")):
        return True
    return len(stripped.split()) < 3


def _build_partial_answer(chunks: list[dict[str, Any]], *, cautious: bool = False) -> str:
    bullet_points: list[str] = []

    for chunk in chunks[:3]:
        sentences = _extract_sentences(chunk.get("content", ""))
        if not sentences:
            continue
        candidate = _sanitize_summary_text(sentences[0])
        if len(candidate) < 25 and len(sentences) > 1:
            candidate = _sanitize_summary_text(f"{candidate} {sentences[1]}")
        if candidate and not _looks_incomplete(candidate) and candidate not in bullet_points:
            bullet_points.append(candidate)

    if not bullet_points:
        return _IDK_RESPONSE

    intro = _PARTIAL_LEADS[0] if cautious else _PARTIAL_LEADS[1]
    bullets = "\n".join(f"- {point}" for point in bullet_points)
    return f"{intro}\n\nHowever, based on the available information:\n\n{bullets}"


def _validate_answer(answer: str, chunks: list[dict[str, Any]]) -> bool:
    normalized_answer = answer.strip()
    if not normalized_answer or normalized_answer == _IDK_RESPONSE:
        return True

    context_text = " ".join(chunk.get("content", "") for chunk in chunks).lower()
    answer_terms = [
        token
        for token in _tokenize(normalized_answer)
        if len(token) > 2 and token not in _VALIDATION_STOPWORDS
    ]
    if not answer_terms:
        return True

    unique_terms = list(dict.fromkeys(answer_terms))
    matched_terms = sum(1 for term in unique_terms if re.search(rf"\b{re.escape(term)}\b", context_text))
    overlap_ratio = matched_terms / len(unique_terms)
    return overlap_ratio >= 0.4 or matched_terms >= min(3, len(unique_terms))


def _contains_unsupported_inference(answer: str, chunks: list[dict[str, Any]]) -> bool:
    normalized_answer = answer.strip().lower()
    if not normalized_answer or normalized_answer == _IDK_RESPONSE.lower():
        return False

    context_text = " ".join(chunk.get("content", "") for chunk in chunks).lower()

    if any(phrase in normalized_answer and phrase not in context_text for phrase in _UNSUPPORTED_INFERENCE_PHRASES):
        return True

    answer_numbers = set(re.findall(r"\b\d+(?:\s*[-–]\s*\d+)?\b", normalized_answer))
    if answer_numbers:
        context_numbers = set(re.findall(r"\b\d+(?:\s*[-–]\s*\d+)?\b", context_text))
        if not answer_numbers.issubset(context_numbers):
            return True

    return False


def _clean_answer_text(answer: str) -> str:
    lines = [line.rstrip() for line in answer.splitlines()]
    cleaned_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue

        if "|" in stripped:
            continue
        if re.search(r"\b(version|page|chunk)\b", stripped, flags=re.IGNORECASE):
            continue

        stripped = re.sub(r"^chunk\s*\d+\s*\|.*$", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\bsource=[^|]+(?:\|\s*)?", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\bpage=\d+\b", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\bversion\s+\S+", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s+", " ", stripped).strip(" |:-")

        if not stripped:
            continue

        if _looks_incomplete(stripped) and not stripped.startswith(("*", "-", "•", "However")):
            continue

        if stripped.startswith(("*", "-", "•")):
            stripped = f"- {stripped.lstrip('*-• ').strip()}"

        cleaned_lines.append(stripped)

    cleaned_text = "\n".join(cleaned_lines).strip()
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
    return cleaned_text


def run_rag_pipeline(query: str, department: str | None = None) -> dict[str, Any]:
    cleaned_query = query.strip()
    cleaned_department = department.strip() if department else None
    if not cleaned_query:
        raise ValueError("Question must not be empty.")

    started_at = perf_counter()

    try:
        query_type = classify_query(cleaned_query)
        if query_type == "meta":
            logger.info("final_decision=meta_response query=%r department=%s", cleaned_query, cleaned_department)
            return {
                "answer": (
                    "I can answer questions based on company documents such as HR policies, SOPs, "
                    "onboarding guides, and engineering docs."
                ),
                "sources": [],
            }

        settings = get_settings()
        logger.info("query_received query=%r department=%s query_type=%s", cleaned_query, cleaned_department, query_type)

        retrieval_result = retrieve_chunks(
            cleaned_query,
            query_type=query_type,
            department=cleaned_department,
            top_k=settings.vector_search_top_k,
        )
        chunks = retrieval_result.chunks

        logger.info(
            "retrieval_decision query_type=%s normalized_query=%r confidence=%s top_score=%s retrieved=%s",
            retrieval_result.query_type,
            retrieval_result.normalized_query,
            retrieval_result.confidence_band,
            round(retrieval_result.top_score, 4) if retrieval_result.top_score is not None else None,
            len(chunks),
        )
        _log_chunk_previews(chunks)
        logger.info(
            "timings embedding=%.3fs retrieval=%.3fs rerank=%.3fs",
            retrieval_result.embedding_time_s,
            retrieval_result.retrieval_time_s,
            retrieval_result.rerank_time_s,
        )

        if not chunks:
            total_time_s = perf_counter() - started_at
            logger.info(
                "final_decision=no_retrieved_chunks top_score=%s total=%.3fs",
                round(retrieval_result.top_score, 4) if retrieval_result.top_score is not None else None,
                total_time_s,
            )
            return {"answer": _IDK_RESPONSE, "sources": []}

        prompt_started_at = perf_counter()
        messages = build_prompt(
            cleaned_query,
            chunks,
            confidence_mode=retrieval_result.confidence_band,
        )
        prompt_time_s = perf_counter() - prompt_started_at

        llm_started_at = perf_counter()
        answer = generate_answer(messages)
        llm_time_s = perf_counter() - llm_started_at
        answer = _clean_answer_text(answer)
        if answer.lower().startswith("i don't know"):
            logger.info("llm_returned_idk_with_chunks=%s replacing_with_partial_answer", len(chunks))
            answer = _build_partial_answer(
                chunks,
                cautious=retrieval_result.confidence_band != "confident",
            )

        if retrieval_result.confidence_band == "cautious" and answer and answer != _IDK_RESPONSE:
            lowered_answer = answer.lower()
            if "not specified" not in lowered_answer and not lowered_answer.startswith("based on the provided context"):
                answer = f"Based on the provided context, {answer[0].lower() + answer[1:]}"

        if _contains_unsupported_inference(answer, chunks):
            logger.info("final_decision=unsupported_inference_detected using_partial_answer")
            answer = _build_partial_answer(
                chunks,
                cautious=retrieval_result.confidence_band != "confident",
            )

        if not _validate_answer(answer, chunks):
            logger.info("final_decision=answer_validation_failed using_partial_answer")
            answer = _build_partial_answer(
                chunks,
                cautious=retrieval_result.confidence_band != "confident",
            )

        answer = _clean_answer_text(answer)

        sources = _build_sources(chunks)
        total_time_s = perf_counter() - started_at
        logger.info(
            "final_decision=answered total=%.3fs embedding=%.3fs retrieval=%.3fs rerank=%.3fs prompt=%.3fs llm=%.3fs source_count=%s",
            total_time_s,
            retrieval_result.embedding_time_s,
            retrieval_result.retrieval_time_s,
            retrieval_result.rerank_time_s,
            prompt_time_s,
            llm_time_s,
            len(sources),
        )

        return {
            "answer": answer,
            "sources": sources,
        }
    except Exception:
        total_time_s = perf_counter() - started_at
        logger.exception("RAG pipeline failed for query=%r after %.3fs", cleaned_query, total_time_s)
        return {
            "answer": "Something went wrong. Please try again.",
            "sources": [],
        }
