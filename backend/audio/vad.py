import torch
from silero_vad import get_speech_timestamps, read_audio

model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    trust_repo=True
)

(get_speech_timestamps, _, _, _, _) = utils

def apply_vad(audio, sr=16000):
    speech_timestamps = get_speech_timestamps(audio, model, sampling_rate=sr)

    speech_segments = []
    for ts in speech_timestamps:
        speech_segments.append(audio[ts['start']:ts['end']])

    return speech_segments
