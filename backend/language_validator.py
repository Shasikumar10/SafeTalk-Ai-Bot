SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu"
}

CONFIDENCE_THRESHOLD = 0.60


def validate_language(stt_result: dict, text_lang: dict | None):
    whisper_lang = stt_result.get("language")
    fasttext_lang = text_lang["language"] if text_lang else None
    confidence = text_lang["confidence"] if text_lang else 0.0

    # Prefer fastText if confident
    final_lang = fasttext_lang if confidence >= CONFIDENCE_THRESHOLD else whisper_lang

    if final_lang not in SUPPORTED_LANGUAGES:
        return {
            "allowed": False,
            "response": {
                "response_type": "unsupported_language",
                "detected_language": final_lang,
                "message": "This language is not supported yet."
            }
        }

    return {
        "allowed": True,
        "language": final_lang
    }
