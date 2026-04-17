from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pypdf import PdfReader


LoadedDocument = dict[str, Any]


def _clean_text(value: str) -> str:
    return "\n".join(line.strip() for line in value.splitlines() if line.strip()).strip()


def load_pdf(pdf_path: Path, department: str) -> list[LoadedDocument]:
    reader = PdfReader(str(pdf_path))
    documents: list[LoadedDocument] = []

    for page_index, page in enumerate(reader.pages, start=1):
        text = _clean_text(page.extract_text() or "")
        if not text:
            continue

        documents.append(
            {
                "content": text,
                "metadata": {
                    "source": pdf_path.name,
                    "department": department,
                    "page": page_index,
                },
            }
        )

    return documents


def load_faq_json(json_path: Path) -> list[LoadedDocument]:
    entries = json.loads(json_path.read_text(encoding="utf-8"))
    documents: list[LoadedDocument] = []

    for index, entry in enumerate(entries, start=1):
        question = _clean_text(str(entry.get("question", "")))
        answer = _clean_text(str(entry.get("answer", "")))
        if not question or not answer:
            continue

        documents.append(
            {
                "content": f"Question: {question}\nAnswer: {answer}",
                "metadata": {
                    "source": json_path.name,
                    "department": "faq",
                    "page": index,
                },
            }
        )

    return documents


def load_all_documents(data_root: Path) -> list[LoadedDocument]:
    documents: list[LoadedDocument] = []
    ordered_departments = ["hr", "onboarding", "engineering", "sop", "operations"]

    for department in ordered_departments:
        for pdf_path in sorted((data_root / department).glob("*.pdf")):
            documents.extend(load_pdf(pdf_path, department))

    faq_path = data_root / "faq" / "faq_data.json"
    if faq_path.exists():
        documents.extend(load_faq_json(faq_path))

    return documents
