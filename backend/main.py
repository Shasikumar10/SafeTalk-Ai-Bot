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
from rag.rag_engine import answer_query_hybrid
from trace import init_trace

app = FastAPI(title="SafeTalk AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class TextInput(BaseModel):
    text: str

@app.get("/")
def health():
    return {"status": "SafeTalk backend running"}

@app.post("/process-text")
async def process_text(payload: TextInput):
    return handle_text_pipeline({"text": payload.text, "language": None})

@app.post("/process-audio")
async def process_audio_endpoint(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        path = tmp.name
    try:
        stt = process_audio(path)
        return handle_text_pipeline(stt)
    finally:
        if os.path.exists(path):
            os.remove(path)

def handle_text_pipeline(stt_result: dict):
    trace = init_trace()
    text = stt_result.get("text", "")

    # Language validation
    validation = validate_language(stt_result)
    trace["language_validation"] = {
    "detected": validation["language"],
    "allowed": validation["allowed"],
    "source": "browser-mic" if stt_result.get("language") is None else "stt-engine"
}


    if not validation["allowed"]:
        return {"response": validation["response"], "trace": trace}

    # Safety
    safety = safety_check(text)
    trace["safety"] = {"triggered": bool(safety)}

    # Intent
    intent = detect_intent(text)
    trace["intent"] = intent

    # Standard responses
    standard = map_response(
        greeting=detect_greeting(text),
        safety=safety,
        intent=intent,
        language=validation["language"]
    )

    trace["standard_response"] = {"triggered": bool(standard)}

    if standard:
        return {"response": standard, "trace": trace}

    # Hybrid RAG
    result = answer_query_hybrid(text, trace)
    trace["rag"] = {
        "mode": result.get("mode"),
        "confidence": result.get("confidence")
    }

    return {
        "question": text,
        "answer": result["answer"],
        "sources": result.get("sources", []),
        "mode": result.get("mode"),
        "trace": trace
    }
