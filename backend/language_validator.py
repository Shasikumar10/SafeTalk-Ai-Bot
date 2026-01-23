"""
3.6 Language Validator
---------------------
Validates detected language with robustness
for short or low-confidence utterances.
"""

SUPPORTED_LANGUAGES = {
    "en": "English"
}

def validate_language(stt_output: dict):
    text = stt_output.get("text", "").strip()
    language = stt_output.get("language")

    # ✅ FIX: Allow short English utterances with unknown language
    if language is None and text:
        return {
            "allowed": True,
            "assumed_language": "en"
        }

    if language not in SUPPORTED_LANGUAGES:
        return {
            "allowed": False,
            "response": {
                "response_type": "unsupported_language",
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
