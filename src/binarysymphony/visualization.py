"""Visualization functionality."""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Optional


class Visualizer:
    """Visualizes musical data."""

    def __init__(self):
        pass

    def plot_notes(
        self, notes: List[Tuple[float, float]], output_file: Optional[str] = None
    ):
        """Plot note frequencies over time."""
        times = []
        freqs = []
        current_time = 0.0
        for freq, duration in notes:
            times.extend([current_time, current_time + duration])
            freqs.extend([freq, freq])
            current_time += duration

        plt.figure(figsize=(10, 6))
        plt.plot(times, freqs)
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency (Hz)")
        plt.title("Note Frequencies Over Time")
        if output_file:
            plt.savefig(output_file)
        else:
            plt.show()

    def plot_spectrogram(
        self, waveform: np.ndarray, sample_rate: int, output_file: Optional[str] = None
    ):
        """Plot spectrogram of the waveform."""
        plt.figure(figsize=(10, 6))
        plt.specgram(waveform, Fs=sample_rate, NFFT=1024, noverlap=512)
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency (Hz)")
        plt.title("Spectrogram")
        if output_file:
            plt.savefig(output_file)
        else:
            plt.show()
