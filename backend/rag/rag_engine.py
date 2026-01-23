from agents.knowledge_builder import build_dynamic_kb
from rag.rag_store import RAGStore
from llm.groq_llm import answer_with_context, answer_general

RAG_THRESHOLD = 0.60

def answer_query_hybrid(query: str, trace: dict):
    docs = build_dynamic_kb(query)

    trace["rag"] = {
        "kb_built": bool(docs),
        "kb_sources": ["Wikipedia", "DuckDuckGo"] if docs else []
    }

    if not docs:
        trace["rag"]["mode"] = "general_llm"
        return {
            "answer": answer_general(query),
            "sources": [],
            "mode": "general_llm"
        }

    store = RAGStore()
    store.build(docs)

    retrieved = store.retrieve_with_scores(query)

    if not retrieved:
        trace["rag"]["mode"] = "general_llm"
        return {
            "answer": answer_general(query),
            "sources": [],
            "mode": "general_llm"
        }

    best_score = max(r["score"] for r in retrieved)
    trace["rag"]["confidence"] = round(best_score, 3)

    if best_score >= RAG_THRESHOLD:
        context = [r["text"] for r in retrieved]
        trace["rag"]["mode"] = "rag"
        return {
            "answer": answer_with_context(context, query),
            "sources": context,
            "mode": "rag"
        }

    trace["rag"]["mode"] = "general_llm"
    return {
        "answer": answer_general(query),
        "sources": [],
        "mode": "general_llm"
    }
