import numpy as np
import librosa
import whisper
import torch

# -----------------------------------
# Load models ONCE
# -----------------------------------

# Whisper STT (for uploaded audio only)
stt_model = whisper.load_model("base")

# Silero VAD (neural VAD)
vad_model, vad_utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    trust_repo=True
)
(get_speech_timestamps, _, _, _, _) = vad_utils


# -----------------------------------
# Noise Suppression (librosa DSP)
# -----------------------------------

def spectral_noise_suppress(
    audio,
    n_fft=1024,
    hop_length=256,
    noise_percentile=20
):
    """
    Spectral gating using librosa (DSP-based).
    """
    # STFT
    stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
    magnitude, phase = np.abs(stft), np.angle(stft)

    # Estimate noise floor from quietest frames
    noise_floor = np.percentile(
        magnitude, noise_percentile, axis=1, keepdims=True
    )

    # Spectral subtraction
    cleaned_mag = np.maximum(magnitude - noise_floor, 0.0)

    # Reconstruct signal
    cleaned_stft = cleaned_mag * np.exp(1j * phase)
    cleaned_audio = librosa.istft(
        cleaned_stft, hop_length=hop_length
    )

    return cleaned_audio.astype(np.float32)


# -----------------------------------
# Full Audio Processing Pipeline
# -----------------------------------

def process_audio(file_path: str):
    """
    Audio File →
    Librosa Noise Suppression →
    Silero VAD →
    Whisper STT
    """

    # 1️⃣ Load audio
    audio, sr = librosa.load(file_path, sr=16000, mono=True)
    audio = audio.astype(np.float32)

    # 2️⃣ Noise suppression (DSP)
    clean_audio = spectral_noise_suppress(audio)

    # 3️⃣ Voice Activity Detection (Silero)
    speech_timestamps = get_speech_timestamps(
        clean_audio,
        vad_model,
        sampling_rate=sr,
        min_silence_duration_ms=150
    )

    if not speech_timestamps:
        return {
            "text": "",
            "language": None
        }

    # 4️⃣ Extract only speech segments
    speech_segments = [
        clean_audio[ts["start"]:ts["end"]]
        for ts in speech_timestamps
    ]

    merged_audio = np.concatenate(speech_segments)

    # 5️⃣ Speech-to-Text (Whisper)
    result = stt_model.transcribe(
        merged_audio,
        fp16=False,
        language="en",
        task="transcribe",
        no_speech_threshold=0.3
    )

    return {
        "text": result["text"].strip(),
        "language": result.get("language")
    }
