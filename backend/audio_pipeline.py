import numpy as np
import soundfile as sf
import noisereduce as nr
import whisper
import torch

# Load models once
stt_model = whisper.load_model("base")

vad_model, vad_utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    trust_repo=True
)
(get_speech_timestamps, _, _, _, _) = vad_utils


def process_audio(file_path: str):
    # Load audio
    audio, sr = sf.read(file_path)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    audio = audio.astype(np.float32)

    # Noise suppression
    clean_audio = nr.reduce_noise(y=audio, sr=sr)

    # VAD
    speech_segments = get_speech_timestamps(clean_audio, vad_model, sampling_rate=sr)
    if not speech_segments:
        return {"text": "", "language": None}

    collected = []
    for seg in speech_segments:
        collected.append(clean_audio[seg["start"]:seg["end"]])

    merged_audio = np.concatenate(collected)

    # STT
    result = stt_model.transcribe(merged_audio, fp16=False)

    return {
        "text": result["text"],
        "language": result.get("language")
    }
