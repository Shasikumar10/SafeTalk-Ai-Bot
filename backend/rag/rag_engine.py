from llm.groq_llm import answer_general, answer_with_context
from agents.knowledge_builder import build_dynamic_kb
from rag.rag_store import RAGStore

rag_store = RAGStore()


def language_instruction(language: str) -> str:
    if language == "te":
        return "Answer ONLY in Telugu."
    if language == "hi":
        return "Answer ONLY in Hindi."
    return "Answer ONLY in English."


def answer_query_hybrid(*, query: str, language: str):
    """
    1. Fetch dynamic knowledge.
    2. Build/update RAGStore.
    3. Retrieve relevant context.
    4. Answer with LLM.
    """
    
    # 1. Fetch info
    docs = build_dynamic_kb(query)
    
    if not docs:
        # Fallback to general LLM if no facts found
        instruction = language_instruction(language)
        prompt = f"{instruction}\n\n{query}"
        answer = answer_general(prompt)
        mode = "general_llm"
        sources = []
    else:
        # 2. Build Store
        rag_store.build(docs)
        
        # 3. Retrieve
        results = rag_store.retrieve_with_scores(query)
        context = [r["text"] for r in results]
        
        # 4. Answer with context
        instruction = language_instruction(language)
        answer = answer_with_context(context, query, instruction=instruction)
        
        mode = "hybrid_rag"
        sources = context

    return {
        "answer": answer,
        "mode": mode,
        "sources": sources
    }
