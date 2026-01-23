import numpy as np
import noisereduce as nr
import whisper
import torch
import librosa

# Load STT model once
stt_model = whisper.load_model("base")

# Load VAD model once
vad_model, vad_utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    trust_repo=True
)
(get_speech_timestamps, _, _, _, _) = vad_utils


def process_audio(file_path: str):
    """
    Audio → Noise Suppression → VAD → STT
    """

    # Load audio safely (any format)
    audio, sr = librosa.load(file_path, sr=16000, mono=True)
    audio = audio.astype(np.float32)

    # Noise Suppression
    clean_audio = nr.reduce_noise(y=audio, sr=sr)

    # Voice Activity Detection
    speech_timestamps = get_speech_timestamps(
        clean_audio,
        vad_model,
        sampling_rate=sr
    )

    if not speech_timestamps:
        return {
            "text": "",
            "language": None
        }

    # Extract speech segments
    segments = [
        clean_audio[ts["start"]:ts["end"]]
        for ts in speech_timestamps
    ]

    merged_audio = np.concatenate(segments)

    # Speech-to-Text
    result = stt_model.transcribe(merged_audio, fp16=False)

    return {
        "text": result["text"].strip(),
        "language": result.get("language")
    }
