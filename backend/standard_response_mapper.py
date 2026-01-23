"""
3.10 Standard Response Mapper
-----------------------------
Centralized deterministic responses for
greetings, safety blocks, and cached queries.
"""

def map_response(
    *,
    greeting=None,
    safety=None,
    intent=None,
):
    """
    Priority order:
    1. Greeting
    2. Safety block
    3. Cached / repeated query
    """

    # 1️⃣ Greeting
    if greeting is not None:
        return {
            "response_type": "standard_greeting",
            "message": "Hello! How can I help you today?"
        }

    # 2️⃣ Safety block
    if safety is not None:
        return {
            "response_type": "standard_safety_block",
            "reason": safety.get("reason", "policy_violation"),
            "category": safety.get("category"),
            "score": safety.get("score"),
            "message": safety.get(
                "message",
                "This request cannot be processed due to safety policies."
            )
        }

    # 3️⃣ Cached / repeated query
    if intent is not None and intent.get("intent") == "repeated_query":
        return {
            "response_type": "cached_response",
            "message": "You asked a similar question earlier. Reusing the cached response.",
            "similarity_score": intent.get("similarity_score")
        }

    # No standard response matched
    return None
