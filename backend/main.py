from fastapi import FastAPI, UploadFile, File
import tempfile
import os

from audio_pipeline import process_audio

app = FastAPI(title="SafeTalk Audio Pipeline")

@app.get("/")
def health():
    return {"status": "SafeTalk backend running"}

@app.post("/process-audio")
async def process(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    result = process_audio(tmp_path)
    os.remove(tmp_path)

    return result
