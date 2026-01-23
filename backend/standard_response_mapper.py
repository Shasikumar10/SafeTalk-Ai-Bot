"""
3.10 Standard Response Mapper
----------------------------
Deterministic, policy-driven response selection.
NO ML. NO randomness.
"""

def map_response(
    greeting: dict | None = None,
    safety: dict | None = None,
    intent: dict | None = None,
    language: str = "en"
):
    """
    Priority order (highest → lowest):
    1. Safety blocks
    2. Greetings
    3. Repeated / non-informational intents
    """

    # -------------------------------------------------
    # 1️⃣ SAFETY HAS HIGHEST PRIORITY
    # -------------------------------------------------
    if safety:
        return {
            "response_type": "safety_block",
            "message": safety.get(
                "message",
                "I can’t help with that request."
            ),
            "details": {
                "category": safety.get("category"),
                "score": safety.get("score")
            }
        }

    # -------------------------------------------------
    # 2️⃣ GREETING (NON-INFORMATIONAL)
    # -------------------------------------------------
    if greeting:
        return {
            "response_type": "standard_greeting",
            "message": greeting["message"]
        }

    # -------------------------------------------------
    # 3️⃣ REPEATED OR LOW-VALUE QUERIES
    # -------------------------------------------------
    if intent:
        if intent.get("intent") == "repeated_query":
            return {
                "response_type": "standard_notice",
                "message": (
                    "You’ve asked a similar question earlier. "
                    "Would you like me to continue from there?"
                )
            }

        if intent.get("intent") == "empty_input":
            return {
                "response_type": "standard_notice",
                "message": "I didn’t catch that. Could you please repeat?"
            }

    # -------------------------------------------------
    # 4️⃣ NO STANDARD RESPONSE → CONTINUE PIPELINE
    # -------------------------------------------------
    return None
