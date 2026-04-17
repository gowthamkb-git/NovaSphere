from __future__ import annotations

import random
import re


_GREETING_PATTERNS = (
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
)

_WELL_BEING_PATTERNS = (
    "how are you",
    "are you fine",
    "how is your day",
    "how's your day",
    "how is it going",
    "how's it going",
)

_HELP_PATTERNS = (
    "can you help me",
    "what can you do",
    "could you help me",
    "how can you help",
    "what are you able to do",
    "what do you help with",
    "can you answer questions",
    "can you answer anything",
)

_CASUAL_PATTERNS = (
    "what's up",
    "whats up",
    "is everything ok",
    "is everything okay",
    "everything good",
    "are you comfortable to answer",
)

_IDENTITY_PATTERNS = (
    "who are you",
    "what do you do",
    "which company you work for",
    "which company do you work for",
    "what company do you work for",
)

_CAPABILITY_PATTERNS = (
    "are you restricted",
    "are you restricted to this company",
    "can you answer anything",
    "can you answer questions",
)

_FRUSTRATION_PATTERNS = (
    "why are you not answering",
    "why are you not answering properly",
    "why not answering properly",
)

_GREETING_RESPONSES = (
    "Hello! How can I assist you today?",
    "Hi there! What can I help you with?",
    "Hey! What would you like help with today?",
    "Hello! I'm here and ready to help.",
)

_WELL_BEING_RESPONSES = (
    "I'm doing well, thanks for asking! How can I help you today?",
    "I'm doing great! Let me know how I can assist you.",
    "I'm doing well and ready to help. What would you like to know?",
    "All good here, thanks! How can I assist you today?",
)

_HELP_RESPONSES = (
    "Of course! I can help you with company policies, onboarding, SOPs, and internal processes.",
    "Yes! Feel free to ask me about policies, onboarding, or company procedures.",
    "Absolutely. I can help with company knowledge like policies, onboarding, and internal processes.",
    "Sure, I can help with company-related questions such as policies, SOPs, and onboarding guidance.",
)

_CASUAL_RESPONSES = (
    "All good here! How can I assist you?",
    "Everything's running smoothly! What would you like help with?",
    "Doing well here. What can I help you with today?",
    "All set on my side. How can I assist you?",
)

_IDENTITY_RESPONSES = (
    "I'm NovaSphere Bot. I assist with company policies, onboarding, SOPs, and internal knowledge.",
    "I'm NovaSphere Bot. I help with company policies, onboarding guidance, SOPs, and internal knowledge.",
)

_CAPABILITY_RESPONSES = (
    "I mainly provide answers based on company knowledge, but I can also help with general questions where possible.",
    "I focus on company knowledge first, and I can also help with general questions when possible.",
)

_FRUSTRATION_RESPONSES = (
    "I'll try my best to help based on available information. If something is unclear, I can still provide related guidance.",
    "I'll do my best to help with the information available. If something is unclear, I can still guide you in the right direction.",
)


def _matches_any(query: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(rf"\b{re.escape(pattern)}\b", query) for pattern in patterns)


def handle_generic(query: str) -> dict:
    lowered_query = query.lower().strip()
    lowered_query = " ".join(lowered_query.split())

    if _matches_any(lowered_query, _FRUSTRATION_PATTERNS):
        answer = random.choice(_FRUSTRATION_RESPONSES)
    elif _matches_any(lowered_query, _IDENTITY_PATTERNS):
        answer = random.choice(_IDENTITY_RESPONSES)
    elif _matches_any(lowered_query, _CAPABILITY_PATTERNS):
        answer = random.choice(_CAPABILITY_RESPONSES)
    elif _matches_any(lowered_query, _WELL_BEING_PATTERNS):
        answer = random.choice(_WELL_BEING_RESPONSES)
    elif _matches_any(lowered_query, _HELP_PATTERNS):
        answer = random.choice(_HELP_RESPONSES)
    elif _matches_any(lowered_query, _CASUAL_PATTERNS):
        answer = random.choice(_CASUAL_RESPONSES)
    elif _matches_any(lowered_query, _GREETING_PATTERNS):
        answer = random.choice(_GREETING_RESPONSES)
    else:
        answer = "I'm here to help with company-related questions. Feel free to ask!"

    return {
        "answer": answer,
        "sources": [],
    }
