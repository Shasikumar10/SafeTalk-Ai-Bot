from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import os

from audio_pipeline import process_audio
from text_language_detector import detect_language_from_text
from language_validator import validate_language
from greeting_detector import detect_greeting
from safety_guard import safety_check
from intent_engine import detect_intent
from standard_response_mapper import map_response
from rag.rag_engine import answer_query_with_agentic_rag
from trace import init_trace


app = FastAPI(title="SafeTalk AI")

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


# ---------------- AUDIO FILE ----------------
@app.post("/process-audio")
async def process_audio_endpoint(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    try:
        stt_result = process_audio(path)
        return handle_text_pipeline(stt_result)
    finally:
        if os.path.exists(path):
            os.remove(path)


# ---------------- LIVE MIC TEXT ----------------
@app.post("/process-text")
async def process_text_endpoint(payload: TextInput):
    stt_result = {
        "text": payload.text,
        "language": None
    }
    return handle_text_pipeline(stt_result)


# ---------------- SHARED PIPELINE ----------------
def handle_text_pipeline(stt_result: dict):
    trace = init_trace()
    text = stt_result.get("text", "")

    # Language detection
    text_lang = detect_language_from_text(text)
    validation = validate_language(stt_result, text_lang)
    trace["language_validation"] = {
        "detected": text_lang,
        "allowed": validation["allowed"]
    }

    if not validation["allowed"]:
        return {
            "response": validation["response"],
            "trace": trace
        }

    # Greeting
    greeting = detect_greeting(text)

    # Safety
    safety = safety_check(text)
    trace["safety"] = {
        "triggered": bool(safety),
        "details": safety
    }

    # Intent
    intent = detect_intent(text)
    trace["intent"] = intent

    # Standard deterministic responses
    standard = map_response(
        greeting=greeting,
        safety=safety,
        intent=intent,
        language=validation["language"]
    )

    trace["standard_response"] = {
        "triggered": bool(standard)
    }

    if standard:
        return {
            "response": standard,
            "trace": trace
        }

    # Hybrid RAG
    rag_result = answer_query_hybrid(text, trace)

    return {
        "question": text,
        "language": validation["language"],
        "answer": rag_result["answer"],
        "sources": rag_result.get("sources", []),
        "mode": rag_result["mode"],
        "trace": trace
    }
