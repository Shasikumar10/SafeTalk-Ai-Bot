import soundfile as sf
import numpy as np

def load_audio_file(file_path: str, target_sr=16000):
    audio, sr = sf.read(file_path)
    
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)  # Convert to mono

    if sr != target_sr:
        raise ValueError("Sample rate must be 16kHz")

    return audio.astype(np.float32)
