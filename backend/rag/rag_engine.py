from llm.groq_llm import answer_general


def language_instruction(language: str) -> str:
    if language == "te":
        return "Answer ONLY in Telugu."
    if language == "hi":
        return "Answer ONLY in Hindi."
    return "Answer ONLY in English."


def answer_query_hybrid(*, query: str, language: str):
    """
    Keyword-only arguments to prevent mismatch bugs.
    """
    instruction = language_instruction(language)
    prompt = f"{instruction}\n\n{query}"

    answer = answer_general(prompt)

    return {
        "answer": answer,
        "mode": "general_llm",
        "sources": []
    }
