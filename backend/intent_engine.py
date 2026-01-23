from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

QUERY_CACHE = []
SIMILARITY_THRESHOLD = 0.85

def detect_intent(text: str):
    text_lower = text.lower().strip()

    if QUERY_CACHE:
        current_embedding = embedding_model.encode([text_lower])
        cached_embeddings = [item["embedding"] for item in QUERY_CACHE]

        similarities = cosine_similarity(
            current_embedding, cached_embeddings
        )[0]

        best_score = max(similarities)

        if best_score >= SIMILARITY_THRESHOLD:
            return {
                "intent": "repeated_query",
                "action": "cached_response",
                "similarity_score": float(best_score)
            }

    embedding = embedding_model.encode([text_lower])[0]
    QUERY_CACHE.append({
        "text": text_lower,
        "embedding": embedding
    })

    return {
        "intent": "new_query",
        "action": "continue"
    }
