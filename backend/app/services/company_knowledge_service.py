from __future__ import annotations

from rag.retrieval.pipeline import run_rag_pipeline


def chat_with_company_knowledge(question: str, department: str | None = None) -> dict:
    return run_rag_pipeline(question, department=department)


def answer_company_question(question: str, department: str | None = None) -> str:
    return chat_with_company_knowledge(question, department=department)["answer"]
