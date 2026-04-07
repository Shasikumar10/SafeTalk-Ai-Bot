import re

GREETING_PATTERNS = [
    r"\bhi\b", r"\bhello\b", r"\bhey\b", 
    r"\bgood morning\b", r"\bgood afternoon\b", r"\bgood evening\b",
    r"\bnamaste\b"
]

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())

def detect_greeting(text: str):
    norm = normalize(text)
    words = norm.split()
    
    if len(words) <= 4:
        for p in GREETING_PATTERNS:
            if re.search(p, norm):
                return {
                    "response_type": "standard_greeting",
                    "message": "Hello! How can I help you today?"
                }
    return None
