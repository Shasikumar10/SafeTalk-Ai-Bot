from fastapi import FastAPI, UploadFile
import tempfile
import os

from audio.audio_input import load_audio_file
from audio.noise_suppressor import suppress_noise
from audio.vad import apply_vad
from audio.stt import transcribe

app = FastAPI()

@app.post("/process-audio/")
async def process_audio(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    audio = load_audio_file(tmp_path)
    audio = suppress_noise(audio)
    speech_segments = apply_vad(audio)
    stt_result = transcribe(speech_segments)

    os.remove(tmp_path)

    return stt_result
