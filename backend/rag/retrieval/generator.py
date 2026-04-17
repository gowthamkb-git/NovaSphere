from __future__ import annotations

from functools import lru_cache

from groq import Groq

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_groq_client() -> Groq:
    api_key = get_settings().groq_api_key.strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set in the environment.")
    return Groq(api_key=api_key)


def generate_answer(messages: list[dict[str, str]]) -> str:
    settings = get_settings()
    response = get_groq_client().chat.completions.create(
        model=settings.groq_model_name,
        temperature=0,
        messages=messages,
    )
    return response.choices[0].message.content.strip()
