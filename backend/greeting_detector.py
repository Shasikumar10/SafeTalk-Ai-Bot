import re

GREETINGS = {
    "hi", "hello", "hey",
    "good morning", "good afternoon", "good evening"
}

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())

def detect_greeting(text: str):
    if normalize(text) in GREETINGS:
        return {
            "response_type": "standard_greeting",
            "message": "Hello! How can I help you today?"
        }
    return None
