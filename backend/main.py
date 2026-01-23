from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile, os

from audio_pipeline import process_audio
from text_language_detector import detect_language_from_text
from language_validator import validate_language
from greeting_detector import detect_greeting
from safety_guard import safety_check
from intent_engine import detect_intent
from standard_response_mapper import map_response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class TextInput(BaseModel):
    text: str


@app.post("/process-audio")
async def process_audio_endpoint(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    try:
        stt_result = process_audio(path)
        return handle_text(stt_result)
    finally:
        os.remove(path)


@app.post("/process-text")
async def process_text_endpoint(payload: TextInput):
    return handle_text({"text": payload.text, "language": None})


def handle_text(stt_result: dict):
    text = stt_result["text"]

    text_lang = detect_language_from_text(text)
    validation = validate_language(stt_result, text_lang)

    if not validation["allowed"]:
        return validation["response"]

    greeting = detect_greeting(text)
    safety = safety_check(text)
    intent = detect_intent(text)

    standard = map_response(
    greeting=greeting,
    safety=safety,
    intent=intent,
    language=validation["language"]
)

if standard:
    return standard


    return {
        "text": text,
        "language": validation["language"],
        "intent_analysis": intent
    }
