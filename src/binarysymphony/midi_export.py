"""MIDI export functionality."""

import numpy as np
from mido import Message, MidiFile, MidiTrack
from typing import List, Tuple


class MidiExporter:
    """Exports notes to MIDI file."""

    def __init__(self):
        pass

    def notes_to_midi(self, notes: List[Tuple[float, float]], output_file: str):
        """Convert notes to MIDI and save."""
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        # Map frequencies back to MIDI notes (approximate)
        def freq_to_midi_note(freq):
            return int(69 + 12 * np.log2(freq / 440.0))

        current_time = 0
        for freq, duration in notes:
            note = freq_to_midi_note(freq)
            track.append(Message("note_on", note=note, velocity=64, time=current_time))
            track.append(
                Message("note_off", note=note, velocity=64, time=int(duration * 480))
            )  # Assuming 120 BPM
            current_time = 0

        mid.save(output_file)
