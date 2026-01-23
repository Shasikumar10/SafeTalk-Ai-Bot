from agents.knowledge_builder import build_dynamic_kb
from rag.rag_store import RAGStore
from llm.groq_llm import answer_with_context, answer_general

RAG_THRESHOLD = 0.60


def answer_query_hybrid(query: str, trace: dict):
    # 🔹 STEP 1: Try to build KB safely
    try:
        docs = build_dynamic_kb(query)
    except Exception as e:
        docs = []
        trace["rag"] = {
            "kb_built": False,
            "kb_error": str(e),
            "mode": "general_llm",
        }

    # 🔹 STEP 2: If KB is empty → General LLM
    if not docs:
        return {
            "mode": "general_llm",
            "answer": answer_general(query),
            "sources": [],
        }

    # 🔹 STEP 3: Normal RAG flow (unchanged)
    try:
        store = RAGStore()
        store.build(docs)

        retrieved = store.retrieve_with_scores(query)

        if not retrieved:
            return {
                "mode": "general_llm",
                "answer": answer_general(query),
                "sources": [],
            }

        best_score = max(r["score"] for r in retrieved)

        if best_score >= RAG_THRESHOLD:
            context = [r["text"] for r in retrieved]
            return {
                "mode": "rag",
                "answer": answer_with_context(context, query),
                "sources": context,
            }

        return {
            "mode": "general_llm",
            "answer": answer_general(query),
            "sources": [],
        }

    except Exception as e:
        return {
            "mode": "error_fallback",
            "answer": "I ran into a temporary issue. Please try again.",
            "sources": [],
        }
