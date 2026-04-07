_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        print("Loading Embedding Model (SentenceTransformers)...")
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

class RAGStore:
    def __init__(self):
        self.index = None
        self.texts = []

    def build(self, docs):
        import faiss
        import numpy as np
        embedder = get_embedder()
        emb = embedder.encode(docs, normalize_embeddings=True)
        dim = emb.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(emb.astype("float32"))
        self.texts = docs

    def retrieve_with_scores(self, query, k=3):
        import numpy as np
        embedder = get_embedder()
        q_emb = embedder.encode([query], normalize_embeddings=True).astype("float32")
        scores, ids = self.index.search(q_emb, k)

        results = []
        for i, s in zip(ids[0], scores[0]):
            if i >= 0:
                results.append({"text": self.texts[i], "score": float(s)})
        return results
