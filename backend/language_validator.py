ALLOWED_LANGUAGES = ["en"]

def validate_language(stt_result: dict):
    language = stt_result.get("language")

    if language not in ALLOWED_LANGUAGES:
        return {
            "allowed": False,
            "response": {
                "error": "unsupported_language",
                "message": "Currently supported language is English only."
            }
        }

    return {
        "allowed": True,
        "response": None
    }
