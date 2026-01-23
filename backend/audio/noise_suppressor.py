import noisereduce as nr
import numpy as np

def suppress_noise(audio: np.ndarray, sr=16000):
    reduced_audio = nr.reduce_noise(
        y=audio,
        sr=sr,
        prop_decrease=0.8
    )
    return reduced_audio.astype(np.float32)
