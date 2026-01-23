import numpy as np
import librosa
import whisper
import torch

# Load Whisper once
stt_model = whisper.load_model("base")

# Load Silero VAD once
vad_model, vad_utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    trust_repo=True
)
(get_speech_timestamps, _, _, _, _) = vad_utils


# ---------------- Noise Suppression (librosa DSP) ----------------
def spectral_noise_suppress(audio, n_fft=1024, hop_length=256):
    stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
    magnitude, phase = np.abs(stft), np.angle(stft)

    noise_floor = np.percentile(magnitude, 20, axis=1, keepdims=True)
    cleaned_mag = np.maximum(magnitude - noise_floor, 0)

    cleaned_stft = cleaned_mag * np.exp(1j * phase)
    return librosa.istft(cleaned_stft, hop_length=hop_length)


# ---------------- Full Audio Pipeline ----------------
def process_audio(file_path: str):
    audio, sr = librosa.load(file_path, sr=16000, mono=True)
    audio = audio.astype(np.float32)

    clean_audio = spectral_noise_suppress(audio)

    speech_timestamps = get_speech_timestamps(
        clean_audio,
        vad_model,
        sampling_rate=sr,
        min_silence_duration_ms=150
    )

    if not speech_timestamps:
        return {"text": "", "language": None}

    speech_segments = [
        clean_audio[ts["start"]:ts["end"]]
        for ts in speech_timestamps
    ]

    merged_audio = np.concatenate(speech_segments)

    # 🔤 Whisper AUTO language detection
    result = stt_model.transcribe(
        merged_audio,
        fp16=False
    )

    return {
        "text": result["text"].strip(),
        "language": result.get("language")
    }
