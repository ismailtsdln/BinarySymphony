"""Audio export functionality."""

import numpy as np
from pydub import AudioSegment
import soundfile as sf


class AudioExporter:
    """Exports waveform to audio files."""

    def __init__(self):
        pass

    def save_wav(self, waveform: np.ndarray, sample_rate: int, output_file: str):
        """Save waveform as WAV."""
        sf.write(output_file, waveform, sample_rate)

    def save_mp3(self, waveform: np.ndarray, sample_rate: int, output_file: str):
        """Save waveform as MP3."""
        # Convert to 16-bit PCM
        waveform_int16 = (waveform * 32767).astype(np.int16)
        audio = AudioSegment(
            waveform_int16.tobytes(), frame_rate=sample_rate, sample_width=2, channels=1
        )
        audio.export(output_file, format="mp3")
