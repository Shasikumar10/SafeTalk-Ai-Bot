from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import os

from audio_pipeline import process_audio
from language_validator import validate_language
from greeting_detector import detect_greeting
from safety_guard import safety_check
from intent_engine import detect_intent
from standard_response_mapper import map_response

app = FastAPI(title="SafeTalk AI – Hybrid Voice Pipeline")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextInput(BaseModel):
    text: str

@app.get("/")
def health():
    return {"status": "SafeTalk backend running"}

# -------------------------
# AUDIO FILE PIPELINE
# -------------------------
@app.post("/process-audio")
async def process_audio_endpoint(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        stt_result = process_audio(tmp_path)
        return handle_text_pipeline(stt_result["text"], stt_result["language"])
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# -------------------------
# LIVE MIC TEXT PIPELINE
# -------------------------
@app.post("/process-text")
async def process_text_endpoint(payload: TextInput):
    return handle_text_pipeline(payload.text, "en")

# -------------------------
# SHARED TEXT PIPELINE
# -------------------------
def handle_text_pipeline(text: str, language: str):
    stt_result = {"text": text, "language": language}

    # 3.6 Language Validator
    validation = validate_language(stt_result)
    if not validation["allowed"]:
        return validation["response"]

    # 3.8 Greeting Detector
    greeting = detect_greeting(text)

    # 3.9 Safety Guard
    safety = safety_check(text)

    # 3.7 Intent
    intent = detect_intent(text)

    # 3.10 Standard Response Mapper
    standard = map_response(
        greeting=greeting,
        safety=safety,
        intent=intent
    )

    if standard:
        return standard

    return {
        "text": text,
        "language": language,
        "intent_analysis": intent
    }
