from __future__ import annotations

import logging
import re

from rag.agents.fallback_agent import handle_fallback
from rag.agents.generic_agent import handle_generic
from rag.retrieval.pipeline import run_rag_pipeline

logger = logging.getLogger(__name__)

_GENERIC_PATTERNS = (
    "hello",
    "hi",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "how are you",
    "are you fine",
    "how is your day",
    "how's your day",
    "can you help me",
    "help me",
    "what can you do",
    "could you help me",
    "what are you able to do",
    "how can you help",
    "who are you",
    "what do you do",
    "which company you work for",
    "which company do you work for",
    "what company do you work for",
    "are you restricted",
    "are you restricted to this company",
    "can you answer questions",
    "can you answer anything",
    "are you comfortable to answer",
    "why are you not answering",
    "why are you not answering properly",
    "is everything ok",
    "is everything okay",
    "what's up",
    "whats up",
    "how's it going",
    "how is it going",
    "thank you",
    "thanks",
)

_RAG_KEYWORDS = (
    "policy",
    "policies",
    "onboarding",
    "sop",
    "process",
    "procedure",
    "leave",
    "benefits",
    "incident",
    "deployment",
    "account setup",
    "hr",
    "engineering",
    "operations",
    "company",
    "document",
    "documents",
    "internal",
    "employee",
)

_RAG_INTENT_PATTERNS = (
    "first day",
    "new employee",
    "new employees",
    "get started",
    "getting started",
    "how onboarding works",
    "how leave works",
    "deployment steps",
    "account setup",
)

_PROCESS_INTENT_PREFIXES = (
    "how do",
    "how does",
    "what should i do",
    "what do i do",
    "where do i start",
)

_COMPANY_HINTS = (
    "company",
    "employee",
    "team",
    "manager",
    "hr",
    "internal",
    "work",
    "office",
    "leave",
    "benefit",
    "joining",
    "onboarding",
    "policy",
)


def classify_query(query: str) -> str:
    lowered_query = query.lower().strip()
    lowered_query = " ".join(lowered_query.split())
    if not lowered_query:
        return "generic"

    if any(re.search(rf"\b{re.escape(pattern)}\b", lowered_query) for pattern in _GENERIC_PATTERNS):
        return "generic"

    if any(re.search(rf"\b{re.escape(keyword)}\b", lowered_query) for keyword in _RAG_KEYWORDS):
        return "rag"

    if any(re.search(rf"\b{re.escape(pattern)}\b", lowered_query) for pattern in _RAG_INTENT_PATTERNS):
        return "rag"

    process_hint_present = any(
        re.search(rf"\b{re.escape(prefix)}\b", lowered_query) for prefix in _PROCESS_INTENT_PREFIXES
    )
    company_process_terms = (
        "onboarding",
        "leave",
        "deployment",
        "policy",
        "process",
        "procedure",
        "account",
        "employee",
        "first day",
        "new employee",
        "get started",
        "joining",
        "setup",
    )
    if process_hint_present and any(
        re.search(rf"\b{re.escape(term)}\b", lowered_query) for term in company_process_terms
    ):
        return "rag"

    if any(re.search(rf"\b{re.escape(hint)}\b", lowered_query) for hint in _COMPANY_HINTS):
        return "rag"

    return "generic"


def handle_rag(query: str, *, department: str | None = None) -> dict:
    return run_rag_pipeline(query, department=department)


def route_query(query: str, *, department: str | None = None) -> dict:
    route = classify_query(query)
    logger.info("Routing query=%r route=%s", query, route)

    if route == "generic":
        logger.info("Generic agent selected for query=%r", query)
        return handle_generic(query)

    if route == "rag":
        result = handle_rag(query, department=department)
        fallback_triggered = result.get("answer") == "I don't know" or not result.get("sources")
        logger.info(
            "RAG agent finished for query=%r fallback_triggered=%s",
            query,
            fallback_triggered,
        )
        if fallback_triggered:
            return handle_fallback()
        return result

    logger.info("Fallback agent selected for query=%r", query)
    return handle_fallback()
