"""
3.8 Greeting Detector
--------------------
Detects greetings and small-talk queries
using deterministic rules with normalization.
"""

import re

GREETINGS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening"
}

STANDARD_GREETING_RESPONSE = {
    "response_type": "standard_greeting",
    "message": "Hello! How can I help you today?"
}

def normalize_text(text: str) -> str:
    # Lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)
    # Collapse whitespace
    text = " ".join(text.split())
    return text

def detect_greeting(text: str):
    if not text:
        return None

    normalized = normalize_text(text)

    if normalized in GREETINGS:
        return STANDARD_GREETING_RESPONSE

    return None
