def map_response(greeting, safety, intent, language):
    """
    Return a deterministic response ONLY for strict cases.
    Otherwise return None to allow RAG / LLM.
    """

    if safety:
        return {
            "response_type": "safety_block",
            "message": "I can’t help with that request, but I’m here if you need safe assistance."
        }

    if greeting:
        return {
            "response_type": "greeting",
            "message": "Hello! How can I help you today?"
        }

    if intent and intent.get("intent") == "follow_up":
        return {
            "response_type": "follow_up",
            "message": "You asked a follow-up. Would you like me to continue from where we left off?"
        }

    return None
