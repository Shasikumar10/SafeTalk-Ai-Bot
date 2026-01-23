from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

from audio_pipeline import process_audio
from language_validator import validate_language
from greeting_detector import detect_greeting
from safety_guard import safety_check
from intent_engine import detect_intent

app = FastAPI(title="SafeTalk AI – Voice Pipeline")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "SafeTalk backend running"}

@app.post("/process-audio")
async def process_audio_endpoint(file: UploadFile = File(...)):
    """
    Pipeline:
    Audio Input
    → Noise Suppression
    → VAD
    → STT
    → Language Validator (3.6)
    → Greeting Detector (3.8)
    → Safety Guard – Detoxify (3.9)
    → Intent & Similarity (3.7)
    """

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # 3.1–3.5
        stt_result = process_audio(tmp_path)

        # 3.6 Language Validator
        validation = validate_language(stt_result)
        if not validation["allowed"]:
            return validation["response"]

        # 3.8 Greeting Detector
        greeting_response = detect_greeting(stt_result["text"])
        if greeting_response:
            return greeting_response

        # 3.9 Safety Guard (Detoxify)
        safety_response = safety_check(stt_result["text"])
        if safety_response:
            return safety_response

        # 3.7 Intent & Similarity
        intent_result = detect_intent(stt_result["text"])

        return {
            "text": stt_result["text"],
            "language": stt_result["language"],
            "intent_analysis": intent_result
        }

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
