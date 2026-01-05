"""Core functionality for mapping binary data to musical notes."""

import numpy as np
from typing import List, Tuple, Dict, Union


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

    # Musical scales (intervals from root)
    SCALES = {
        "chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # All 12 notes
        "major": [0, 2, 4, 5, 7, 9, 11],  # W W H W W W H
        "minor": [0, 2, 3, 5, 7, 8, 10],  # W H W W H W W
        "pentatonic": [0, 2, 4, 7, 9],  # Major pentatonic
        "blues": [0, 3, 5, 6, 7, 10],  # Blues scale
        "dorian": [0, 2, 3, 5, 7, 9, 10],  # Dorian mode
        "phrygian": [0, 1, 3, 5, 7, 8, 10],  # Phrygian mode
    }

    def __init__(self, mode: str = "melody", scale: str = "chromatic"):
        self.mode = mode
        self.scale = scale
        if scale not in self.SCALES:
            raise ValueError(
                f"Unknown scale: {scale}. Available: {list(self.SCALES.keys())}"
            )

    def map_bytes_to_notes(self, data: bytes) -> List[Tuple[float, float]]:
        """Map bytes to (frequency, duration) pairs."""
        notes = []
        scale_notes = self.SCALES[self.scale]
        note_names = list(self.NOTES.keys())

        for i, byte in enumerate(data):
            # Map byte to scale index
            scale_index = byte % len(scale_notes)
            note_index = scale_notes[scale_index]

            # Calculate octave (0-8 range for more variety)
            octave = 3 + (byte // len(scale_notes)) % 6

            # Get note name and frequency
            note_name = note_names[note_index]
            freq = self.NOTES[note_name] * (2 ** (octave - 4))

            # Duration based on mode
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

    def process_batch(
        self,
        input_files: List[str],
        output_dir: str,
        output_format: str = "wav",
        progress_callback=None,
    ) -> List[Dict[str, Union[str, None]]]:
        """Process multiple files in batch.

        Args:
            input_files: List of input file paths
            output_dir: Output directory path
            output_format: Output format (wav, mp3, midi, spectrum)
            progress_callback: Optional callback function for progress updates

        Returns:
            List of dicts with 'input', 'output', 'status', 'error' keys
        """
        results = []
        total_files = len(input_files)

        for i, input_file in enumerate(input_files):
            result = {
                "input": input_file,
                "output": None,
                "status": "pending",
                "error": None,
            }

            try:
                # Generate output filename
                from pathlib import Path

                input_path = Path(input_file)
                output_name = f"{input_path.stem}_binarysymphony.{output_format}"
                output_path = Path(output_dir) / output_name

                # Read and process file
                with open(input_path, "rb") as f:
                    data = f.read()

                if not data:
                    result["status"] = "error"
                    result["error"] = "File is empty"
                    results.append(result)
                    continue

                # Map to notes
                notes = self.map_bytes_to_notes(data)

                # Export based on format
                if output_format == "midi":
                    from .midi_export import MidiExporter

                    exporter = MidiExporter()
                    exporter.notes_to_midi(notes, str(output_path))
                elif output_format in ["wav", "mp3"]:
                    waveform = self.generate_waveform(notes)
                    from .audio_export import AudioExporter

                    audio_exporter = AudioExporter()
                    if output_format == "wav":
                        audio_exporter.save_wav(waveform, 44100, str(output_path))
                    else:
                        audio_exporter.save_mp3(waveform, 44100, str(output_path))
                elif output_format == "spectrum":
                    waveform = self.generate_waveform(notes)
                    from .visualization import Visualizer

                    visualizer = Visualizer()
                    visualizer.plot_spectrogram(waveform, 44100, str(output_path))

                result["output"] = str(output_path)
                result["status"] = "success"

            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)

            results.append(result)

            # Progress callback
            if progress_callback:
                progress_callback(i + 1, total_files, result)

        return results
