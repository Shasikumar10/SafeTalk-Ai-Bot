"""
3.8 Greeting Detector
--------------------
Detects greetings and small-talk queries
using deterministic rules.
"""

GREETINGS = {
    "hi", "hello", "hey",
    "good morning",
    "good afternoon",
    "good evening"
}

STANDARD_GREETING_RESPONSE = {
    "response_type": "greeting",
    "message": "Hello! How can I help you today?"
}

def detect_greeting(text: str):
    if not text:
        return None

    text_clean = text.lower().strip()

    if text_clean in GREETINGS:
        return STANDARD_GREETING_RESPONSE

    return None
