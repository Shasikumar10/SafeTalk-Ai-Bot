from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")
CACHE = []
THRESHOLD = 0.85

def detect_intent(text: str):
    emb = model.encode([text])[0]

    if CACHE:
        sims = cosine_similarity([emb], [c["emb"] for c in CACHE])[0]
        if max(sims) >= THRESHOLD:
            return {"intent": "repeated_query"}

    CACHE.append({"text": text, "emb": emb})
    return {"intent": "new_query"}
