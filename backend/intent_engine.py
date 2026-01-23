from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def detect_intent(text: str):
    text = text.lower()

    follow_up_phrases = [
        "continue",
        "same as before",
        "go on",
        "as mentioned",
        "earlier question"
    ]

    if any(p in text for p in follow_up_phrases):
        return {"intent": "follow_up"}

    return {"intent": "new_query"}
