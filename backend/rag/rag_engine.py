from agents.knowledge_builder import build_dynamic_kb
from rag.rag_store import RAGStore
from llm.groq_llm import answer_with_context


def answer_query_with_agentic_rag(query: str):
    # 1️⃣ Agent builds KB
    documents = build_dynamic_kb(query)

    if not documents:
        return {
            "answer": "I don't know",
            "sources": []
        }

    # 2️⃣ Build temporary vector store
    store = RAGStore()
    store.build(documents)

    # 3️⃣ Retrieve relevant chunks
    retrieved = store.retrieve(query)

    # 4️⃣ LLM answers strictly from retrieved context
    answer = answer_with_context(retrieved, query)

    return {
        "answer": answer,
        "sources": retrieved
    }
