from __future__ import annotations

from typing import Any

SYSTEM_PROMPT = (
    "You are an internal company assistant. "
    "Your job is to provide clear, helpful, and natural answers using ONLY the provided context. "
    "Use ONLY the provided context. "
    "Do NOT invent facts or numbers. "
    "If an exact detail is missing, mention it briefly in one line only. "
    "Then provide the best possible helpful explanation using available information. "
    "Summarize and interpret instead of copying raw text. "
    "NEVER include document metadata such as version, page, or chunk numbers. "
    "Keep answers clean, readable, and structured. "
    "Use bullet points where useful. "
    "Make the response feel like a human assistant, not a document."
)


def _format_context_chunk(chunk: dict[str, Any], index: int) -> str:
    metadata = chunk.get("metadata", {})
    source = metadata.get("source", "unknown")
    page = metadata.get("page")
    header_parts = [f"Chunk {index}", f"source={source}"]
    if page is not None:
        header_parts.append(f"page={page}")

    header = " | ".join(header_parts)
    return f"{header}\n{chunk.get('content', '').strip()}"


def build_prompt(
    question: str,
    chunks: list[dict[str, Any]],
    *,
    confidence_mode: str = "confident",
) -> list[dict[str, str]]:
    context = "\n\n".join(_format_context_chunk(chunk, index) for index, chunk in enumerate(chunks, start=1))
    confidence_instruction = (
        "The retrieved context is only moderately strong. If needed, mention briefly that a detail is not explicit, then give the most helpful grounded explanation supported by the context."
        if confidence_mode == "cautious"
        else "Use the context to give the clearest grounded answer possible without adding unstated facts."
    )
    user_prompt = (
        "You are an internal company assistant.\n\n"
        "Your job is to provide clear, helpful, and natural answers using ONLY the provided context.\n\n"
        "Rules:\n"
        "* Use ONLY the provided context\n"
        "* Do NOT invent facts or numbers\n"
        "* If exact detail is missing, mention it briefly in one line only\n"
        "* Then provide the best possible helpful explanation using available information\n"
        "* Summarize and interpret, DO NOT copy raw text\n"
        "* NEVER include document metadata such as version, page, or chunk in the answer\n"
        "* Keep answers clean, readable, and structured\n"
        "* Use bullet points where helpful\n"
        "* Make the response feel like a human assistant, not a document\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question.strip()}\n\n"
        "Response style:\n"
        "* If the full answer is available, give a clean explanation and use bullets if helpful\n"
        "* If the answer is partial, briefly mention the exact detail is not explicit, then summarize the most relevant grounded points from the context\n"
        "* Do not mention unsupported conclusions such as company type, financial status, or missing details that are not stated\n"
        "* Do not quote the context directly unless a short phrase is necessary\n"
        "* Keep the tone natural and helpful\n\n"
        f"{confidence_instruction}\n\n"
        "Answer:"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
