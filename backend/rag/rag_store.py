import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")


class RAGStore:
    def __init__(self):
        self.index = None
        self.chunks = []

    def build(self, documents: list[str]):
        embeddings = embedder.encode(documents)
        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(embeddings).astype("float32"))
        self.chunks = documents

    def retrieve(self, query: str, top_k=2):
        q_emb = embedder.encode([query]).astype("float32")
        distances, indices = self.index.search(q_emb, top_k)

        return [self.chunks[i] for i in indices[0]]
