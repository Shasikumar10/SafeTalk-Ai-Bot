import fasttext
import os

MODEL_PATH = os.path.join("models", "lid.176.bin")

lang_model = fasttext.load_model(MODEL_PATH)


def detect_language_from_text(text: str):
    if not text.strip():
        return None

    labels, scores = lang_model.predict(text, k=1)
    return {
        "language": labels[0].replace("__label__", ""),
        "confidence": float(scores[0])
    }
