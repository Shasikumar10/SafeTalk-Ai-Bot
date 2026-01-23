"""
3.6 Language Validator
---------------------
Checks whether the detected language from STT
is supported by the system.
"""

SUPPORTED_LANGUAGES = {
    "en": "English"
}

def validate_language(stt_output: dict):
    """
    Input:
        stt_output = {
            "text": "...",
            "language": "en"
        }

    Output (allowed):
        {
            "allowed": True
        }

    Output (blocked):
        {
            "allowed": False,
            "response": {...}
        }
    """

    language = stt_output.get("language")

    if language not in SUPPORTED_LANGUAGES:
        return {
            "allowed": False,
            "response": {
                "error": "unsupported_language",
                "message": (
                    "I currently support English only. "
                    "Please ask your question in English."
                ),
                "detected_language": language
            }
        }

    return {
        "allowed": True
    }
