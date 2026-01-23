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
# Language detection
# -------------------------
def detect_language(text: str) -> str:
    for ch in text:
        if "\u0C00" <= ch <= "\u0C7F":
            return "te"
        if "\u0900" <= ch <= "\u097F":
            return "hi"
    return "en"


# -------------------------
# Normalize query
# -------------------------
def normalize_query(text: str) -> str:
    fillers = ["uh", "um", "like", "you know"]
    for f in fillers:
        text = text.replace(f, "")
    return text.strip()


# -------------------------
# API
# -------------------------
@app.post("/process-audio")
async def process_audio_endpoint(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        audio_path = tmp.name

    try:
        clean_audio = process_audio(audio_path)
        if not clean_audio:
            return {
                "answer": "I couldn’t hear you clearly. Please try again.",
                "language": "en",
                "mode": "stt_low_confidence"
            }

        # STT
        text = transcribe_audio(clean_audio)
        if not text or len(text.split()) < 2:
            return {
                "answer": "I couldn’t hear you clearly. Please try again.",
                "language": "en",
                "mode": "stt_low_confidence"
            }

        text = normalize_query(text)
        language = detect_language(text)

        # RAG + LLM
        result = answer_query_hybrid(
            query=text,
            language=language
        )

        result["language"] = language
        return result

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
