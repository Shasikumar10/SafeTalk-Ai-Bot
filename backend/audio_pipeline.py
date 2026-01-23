import torch
import librosa
import numpy as np
import tempfile
import os
import noisereduce as nr
import soundfile as sf

# =========================
# Load Silero VAD
# =========================
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


# =========================
# Merge nearby speech segments
# =========================
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


# =========================
# Main audio processing pipeline
# =========================
def process_audio(file_path: str, sample_rate: int = 16000):
    """
    Steps:
    1. Load audio
    2. Noise suppression (librosa + noisereduce)
    3. Voice Activity Detection (Silero)
    4. Merge speech segments
    5. Return clean speech audio
    """

    # 1️⃣ Load audio
    audio, sr = librosa.load(file_path, sr=sample_rate, mono=True)

    # 2️⃣ Noise suppression
    reduced_noise = nr.reduce_noise(
        y=audio,
        sr=sr,
        prop_decrease=0.9
    )

    # Convert to torch tensor for VAD
    audio_tensor = torch.from_numpy(reduced_noise).float()

    # 3️⃣ Voice Activity Detection (tuned)
    speech_timestamps = get_speech_timestamps(
        audio_tensor,
        vad_model,
        threshold=0.3,                  # less aggressive
        min_speech_duration_ms=500,     # wait before cutting
        min_silence_duration_ms=800     # allow pauses
    )

    if not speech_timestamps:
        return None  # No speech detected

    # 4️⃣ MERGE SEGMENTS (THIS IS THE KEY FIX)
    speech_timestamps = merge_segments(speech_timestamps)

    # 5️⃣ Collect speech chunks
    speech_audio = collect_chunks(
        speech_timestamps,
        audio_tensor
    )

    # Save processed speech to temp WAV
    tmp_wav = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    )
    sf.write(tmp_wav.name, speech_audio.numpy(), sr)

    return tmp_wav.name
