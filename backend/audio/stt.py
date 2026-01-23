import whisper
import numpy as np

model = whisper.load_model("base")

def transcribe(audio_segments, sr=16000):
    full_text = []
    detected_language = None

    for segment in audio_segments:
        result = model.transcribe(segment, fp16=False)
        full_text.append(result["text"])

        if not detected_language:
            detected_language = result.get("language")

    return {
        "text": " ".join(full_text),
        "language": detected_language
    }
