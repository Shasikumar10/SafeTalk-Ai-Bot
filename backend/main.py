from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import os

from audio_pipeline import process_audio, transcribe_audio
from rag.rag_engine import answer_query_hybrid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Utilities
# -------------------------
def init_trace():
    return {
        "audio": {},
        "stt": {},
        "rag": {},
    }


def normalize_query(text: str) -> str:
    fillers = ["uh", "um", "like", "you know"]
    for f in fillers:
        text = text.replace(f, "")
    return text.strip()


# -------------------------
# Request Models
# -------------------------
class TextPayload(BaseModel):
    text: str


# -------------------------
# Routes
# -------------------------
@app.post("/process-audio")
async def process_audio_endpoint(file: UploadFile = File(...)):
    trace = init_trace()

    # Save uploaded audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        audio_path = tmp.name

    try:
        # Audio pipeline (noise + VAD)
        clean_audio_path = process_audio(audio_path)

        if not clean_audio_path:
            return {
                "mode": "stt_low_confidence",
                "answer": "I didn’t catch that clearly. Could you please repeat?",
                "sources": [],
            }

        # Speech → Text
        text = transcribe_audio(clean_audio_path, language="en-IN")
        trace["stt"]["text"] = text

        # Confidence guard
        if not text or len(text.split()) < 3:
            return {
                "mode": "stt_low_confidence",
                "answer": "I didn’t catch that clearly. Could you please repeat?",
                "sources": [],
            }

        # Normalize
        text = normalize_query(text)

        # RAG / LLM
        result = answer_query_hybrid(text, trace)
        return result

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


@app.post("/process-text")
async def process_text(payload: TextPayload):
    trace = init_trace()

    text = payload.text.strip()
    if not text:
        return {
            "mode": "empty",
            "answer": "Please say or type something.",
            "sources": [],
        }

    text = normalize_query(text)
    result = answer_query_hybrid(text, trace)
    return result
