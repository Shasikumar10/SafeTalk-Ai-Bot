import torch
import librosa
import numpy as np
import tempfile
import os
import noisereduce as nr
import soundfile as sf
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
# Load Silero VAD
vad_model, vad_utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    force_reload=False
)

(
    get_speech_timestamps,
    save_audio,
    read_audio,
    VADIterator,
    collect_chunks
) = vad_utils


# Merge nearby speech segments
def merge_segments(segments, max_gap=0.8):
    """
    Merge speech segments if silence gap is small.
    Fixes early cutoff and mid-sentence pauses.
    """
    merged = []
    for seg in segments:
        if not merged:
            merged.append(seg)
            continue

        gap = seg["start"] - merged[-1]["end"]
        if gap < max_gap:
            merged[-1]["end"] = seg["end"]
        else:
            merged.append(seg)

    return merged


# Main audio processing pipeline
def process_audio(file_path: str, sample_rate: int = 16000):
    """
    Steps:
    1. Load audio
    2. Noise suppression (librosa + noisereduce)
    3. Voice Activity Detection (Silero)
    4. Merge speech segments
    5. Return clean speech audio
    """

    # 1Load audio
    audio, sr = librosa.load(file_path, sr=sample_rate, mono=True)
    
    # Normalize audio
    audio = librosa.util.normalize(audio)

    #  Apply AI noise reduction to clean static/hums
    audio = nr.reduce_noise(y=audio, sr=sr, prop_decrease=0.85)

    # Convert to torch tensor for VAD
    audio_tensor = torch.from_numpy(audio).float()

    #  Voice Activity Detection (tuned for sensitivity)
    speech_timestamps = get_speech_timestamps(
        audio_tensor,
        vad_model,
        threshold=0.2,                   
        min_speech_duration_ms=250,      
        min_silence_duration_ms=1000      
    )

    if not speech_timestamps:
        return None  

    speech_timestamps = merge_segments(speech_timestamps)

    speech_audio = collect_chunks(
        speech_timestamps,
        audio_tensor
    )

    tmp_wav = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    )
    sf.write(tmp_wav.name, speech_audio.numpy(), sr)

    return tmp_wav.name

def transcribe_audio(audio_path, language="en-IN"):
    """
    Robust transcription using Groq Whisper API
    """
    if not groq_client: return ""
    try:
        with open(audio_path, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=(audio_path, file.read()),
                model="whisper-large-v3",
                response_format="json"
            )
        return transcription.text.strip()
    except Exception as e:
        print(f"Groq Whisper error: {e}")
        return ""