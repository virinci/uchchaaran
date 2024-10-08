import librosa
import numpy as np
import soundfile
from pathlib import Path
import re


def calculate_syllable_intervals(audio_frames, frame_length, hop_length, threshold):
    # Use short-time energy to find non-silent parts
    # Adjust the frame_length and hop_length depending on the nature of the audio
    frames = librosa.util.frame(
        audio_frames, frame_length=frame_length, hop_length=hop_length
    )
    energy = np.sum(frames**2, axis=0)

    # Normalize energy
    energy /= np.max(energy)

    # Threshold for energy to detect syllables
    syllable_frames = np.where(energy > threshold)[0]

    # Group consecutive frames to identify syllable boundaries
    syllable_intervals = []
    prev = syllable_frames[0]
    start = syllable_frames[0]

    for frame in syllable_frames[1:]:
        if frame != prev + 1:
            syllable_intervals.append((start, prev))
            start = frame
        prev = frame
    syllable_intervals.append((start, prev))

    # Convert intervals from frame index to time in samples
    syllable_intervals_in_samples = [
        (int(start * hop_length), int(end * hop_length))
        for start, end in syllable_intervals
    ]

    return syllable_intervals_in_samples


def split_and_save_audio(file_path: Path, expected: int):
    audio_frames, sample_rate = librosa.load(file_path, sr=None)

    frame_length, hop_length = 2048, 512
    threshold = 0.01

    while threshold <= 0.15:
        threshold += 0.01

        syllable_intervals_in_samples = calculate_syllable_intervals(
            audio_frames, frame_length, hop_length, threshold
        )

        if len(syllable_intervals_in_samples) != expected:
            continue

        # Extract syllables and save them as separate wave files
        for idx, (start_sample, end_sample) in enumerate(syllable_intervals_in_samples):
            syllable = audio_frames[start_sample:end_sample]
            output_filename = f"./data/devanagari_syllable_dataset_split/{file_path.stem}_{idx + 1:02}.wav"
            soundfile.write(output_filename, syllable, sample_rate)
            print(f"Wrote {output_filename}")
        break


file_paths = (Path(__file__).parent / "./data/devanagari_syllable_dataset").glob(
    "*.m4a"
)

for file_path in file_paths:
    if (m := re.match(r"(\w+)_(\d+)", file_path.stem)) is None:
        continue

    name, no = m.groups()
    no = int(no)

    match no:
        case 16:
            expected = 10
        case _:
            expected = 20

    split_and_save_audio(file_path, expected)
