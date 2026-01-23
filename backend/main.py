from fastapi import FastAPI, UploadFile, File
import tempfile
import os

from audio_pipeline import process_audio
from language_validator import validate_language

app = FastAPI(title="SafeTalk Audio Pipeline")

@app.get("/")
def health_check():
    return {"status": "SafeTalk backend is running"}

@app.post("/process-audio")
async def process_audio_endpoint(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Run audio pipeline
    result = process_audio(tmp_path)

    # Delete temp file
    os.remove(tmp_path)

    # Language validation
    validation = validate_language(result)
    if not validation["allowed"]:
        return validation["response"]

    return result
