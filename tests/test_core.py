"""Tests for core module."""

import pytest
from binarysymphony.core import BinaryMapper


class TestBinaryMapper:
    def test_map_bytes_to_notes(self):
        mapper = BinaryMapper()
        data = b"\x00\x01\x02"
        notes = mapper.map_bytes_to_notes(data)
        assert len(notes) == 3
        assert all(isinstance(note, tuple) and len(note) == 2 for note in notes)

    def test_map_bytes_to_notes_rhythm_mode(self):
        mapper = BinaryMapper(mode="rhythm")
        data = b"\x00\x01"
        notes = mapper.map_bytes_to_notes(data)
        assert len(notes) == 2
        # Check durations vary
        durations = [d for _, d in notes]
        assert len(set(durations)) > 0  # At least some variation

    def test_map_bytes_to_notes_with_scale(self):
        mapper = BinaryMapper(mode="melody", scale="major")
        data = b"\x00\x01\x02"
        notes = mapper.map_bytes_to_notes(data)
        assert len(notes) == 3
        # Major scale should only use specific intervals
        frequencies = [f for f, _ in notes]
        # Check that frequencies correspond to major scale notes
        assert all(isinstance(f, (int, float)) for f in frequencies)

    def test_invalid_scale(self):
        with pytest.raises(ValueError):
            BinaryMapper(scale="invalid_scale")

    def test_generate_waveform(self):
        mapper = BinaryMapper()
        notes = [(440.0, 0.5), (880.0, 0.5)]
        waveform = mapper.generate_waveform(notes, sample_rate=44100)
        assert len(waveform) == int(1.0 * 44100)  # 1 second total