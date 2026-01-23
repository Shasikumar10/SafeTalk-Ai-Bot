SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu"
}

def validate_language(stt_result: dict):
    detected = stt_result.get("language")

    # ✅ FIX: live mic does not provide language → assume English
    if detected is None:
        detected = "en"

    if detected not in SUPPORTED_LANGUAGES:
        return {
            "allowed": False,
            "response": {
                "response_type": "unsupported_language",
                "detected_language": detected,
                "message": "This language is not supported yet."
            }
        }

    return {
        "allowed": True,
        "language": detected
    }
