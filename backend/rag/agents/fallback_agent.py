from __future__ import annotations


def handle_fallback() -> dict:
    return {
        "answer": (
            "I don't have this information right now.\n\n"
            "You can contact HR at [hr@nova.com](mailto:hr@nova.com)"
        ),
        "sources": [],
    }
