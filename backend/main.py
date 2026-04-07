import os
import io
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://safetalkai.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "SafeTalk AI is live"}


def detect_language(text: str) -> str:
    for ch in text:
        if "\u0C00" <= ch <= "\u0C7F":
            return "te"
        if "\u0900" <= ch <= "\u097F":
            return "hi"
    return "en"


def normalize_query(text: str) -> str:
    fillers = ["uh", "um", "like", "you know"]
    for f in fillers:
        text = text.replace(f, "")
    return text.strip()


@app.post("/process-audio")
async def process_audio_endpoint(file: UploadFile = File(...)):
    # SUPER LAZY IMPORTS - Loads only on first request to survive Render's port scan
    from pydub import AudioSegment
    from audio_pipeline import process_audio, transcribe_audio
    from language_validator import validate_language
    from intent_engine import detect_intent
    from greeting_detector import detect_greeting
    from safety_guard import safety_check
    from standard_response_mapper import map_response
    from rag.rag_engine import answer_query_hybrid

    content = await file.read()
    if not content:
        return {"answer": "No audio data received.", "mode": "error"}

    audio_path = None
    try:
        # Load audio from memory using BytesIO
        try:
            audio = AudioSegment.from_file(io.BytesIO(content))
        except Exception as e:
            print(f"Error loading audio: {e}")
            return {"answer": "Error reading audio file format.", "mode": "error"}
        
        audio = audio.set_frame_rate(16000).set_channels(1)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            audio.export(tmp.name, format="wav")
            audio_path = tmp.name

        clean_audio = process_audio(audio_path)
        if not clean_audio:
            return {
                "answer": "I couldn’t hear you clearly. Please try again.",
                "language": "en",
                "mode": "stt_low_confidence"
            }

        # STT
        text = transcribe_audio(clean_audio)
        if not text:
            return {
                "answer": "I couldn’t hear you clearly. Please try again.",
                "language": "en",
                "mode": "stt_low_confidence"
            }

        text = normalize_query(text)
        language = detect_language(text)

        # 1. Language Validator
        lang_validation = validate_language({"language": language})
        if not lang_validation.get("allowed"):
            return {
                "answer": lang_validation["response"]["message"],
                "language": language,
                "mode": lang_validation["response"]["response_type"],
                "text": text
            }

        # 2. Detectors (Intent, Greeting, Safety)
        intent_result = detect_intent(text)
        greeting_result = detect_greeting(text)
        safety_result = safety_check(text)

        # 3. Orchestration Branch
        standard_response = map_response(
            greeting=greeting_result,
            safety=safety_result,
            intent=intent_result,
            language=language
        )

        if standard_response:
            return {
                "answer": standard_response["message"],
                "language": language,
                "mode": standard_response["response_type"],
                "text": text
            }

        # RAG + LLM Engine
        result = answer_query_hybrid(
            query=text,
            language=language
        )

        result["language"] = language
        result["text"] = text
        return result

    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
