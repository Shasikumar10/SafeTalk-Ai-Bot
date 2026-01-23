from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

from audio_pipeline import process_audio
from language_validator import validate_language
from greeting_detector import detect_greeting
from safety_guard import safety_check
from intent_engine import detect_intent
from standard_response_mapper import map_response

app = FastAPI(title="SafeTalk AI – Voice Pipeline")

# CORS
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
    → Safety Guard (3.9)
    → Standard Response Mapper (3.10)
    → Intent & Similarity (3.7)
    """

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # 3.1–3.5 Speech pipeline
        stt_result = process_audio(tmp_path)

        # 3.6 Language Validator
        validation = validate_language(stt_result)
        if not validation["allowed"]:
            return validation["response"]

        # 3.8 Greeting Detector
        greeting = detect_greeting(stt_result["text"])

        # 3.9 Safety Guard
        safety = safety_check(stt_result["text"])

        # 3.7 Intent & Similarity
        intent = detect_intent(stt_result["text"])

        # 3.10 Standard Response Mapper
        standard_response = map_response(
            greeting=greeting,
            safety=safety,
            intent=intent
        )

        if standard_response:
            return standard_response

        # No standard response → pass through
        return {
            "text": stt_result["text"],
            "language": stt_result["language"],
            "intent_analysis": intent
        }

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
