"""Core functionality for mapping binary data to musical notes."""

import numpy as np
from typing import List, Tuple


class BinaryMapper:
    """Maps binary data to musical notes."""

    # Note frequencies in Hz (A4 = 440 Hz)
    NOTES = {
        "C": 261.63,
        "C#": 277.18,
        "D": 293.66,
        "D#": 311.13,
        "E": 329.63,
        "F": 349.23,
        "F#": 369.99,
        "G": 392.00,
        "G#": 415.30,
        "A": 440.00,
        "A#": 466.16,
        "B": 493.88,
    }

    def __init__(self, mode: str = "melody"):
        self.mode = mode

    def map_bytes_to_notes(self, data: bytes) -> List[Tuple[float, float]]:
        """Map bytes to (frequency, duration) pairs."""
        notes = []
        for i, byte in enumerate(data):
            # Map byte (0-255) to note index
            note_index = byte % 12
            octave = 4 + (byte // 12) % 4  # Octaves 4-7
            note_name = list(self.NOTES.keys())[note_index]
            freq = self.NOTES[note_name] * (2 ** (octave - 4))
            
            if self.mode == "melody":
                duration = 0.5
            elif self.mode == "rhythm":
                duration = 0.25 + (byte % 4) * 0.25  # Variable duration
            elif self.mode == "spectrum":
                duration = 0.1  # Shorter for spectrum analysis
            else:
                duration = 0.5
            
            notes.append((freq, duration))
        return notes

    def generate_waveform(
        self, notes: List[Tuple[float, float]], sample_rate: int = 44100
    ) -> np.ndarray:
        """Generate audio waveform from notes."""
        total_samples = 0
        for _, duration in notes:
            total_samples += int(duration * sample_rate)

        waveform = np.zeros(total_samples)
        current_sample = 0

        for freq, duration in notes:
            samples = int(duration * sample_rate)
            t = np.linspace(0, duration, samples, False)
            wave = 0.5 * np.sin(2 * np.pi * freq * t)  # Sine wave
            waveform[current_sample : current_sample + samples] = wave
            current_sample += samples

        return waveform
