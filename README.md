# BinarySymphony

[![CI](https://github.com/ismailtsdln/BinarySymphony/actions/workflows/ci.yml/badge.svg)](https://github.com/ismailtsdln/BinarySymphony/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/binarysymphony)](https://pypi.org/project/binarysymphony/)

Convert binary files into musical symphonies! Transform any binary data (executables, images, documents) into audible music by mapping byte values to musical notes.

## Features

- **Multiple Output Formats**: Generate WAV, MP3, or MIDI files from binary data
- **Flexible Mapping Modes**: Choose from melody, rhythm, or spectrum modes
- **Command-Line Interface**: Easy-to-use CLI with comprehensive options and rich UI
- **Graphical User Interface**: Interactive PyQt6-based GUI for visual control
- **Visualization**: Generate spectrograms and note frequency plots
- **Rich Terminal UI**: Colorful output, progress bars, and user-friendly messages
- **Robust Error Handling**: Comprehensive input validation and error checking
- **Modular Architecture**: Clean, extensible codebase ready for PyPI packaging

## Installation

### From PyPI (Recommended)

```bash
pip install binarysymphony
```

### From Source

```bash
git clone https://github.com/ismailtsdln/BinarySymphony.git
cd BinarySymphony
pip install -e .
```

## Dependencies

- Python >= 3.8
- pydub
- pygame
- mido
- numpy
- matplotlib
- PyQt6
- rich

## Usage

### Command-Line Interface

The CLI features a rich, colorful interface with progress bars and user-friendly messages.

```bash
binarysymphony --input myfile.exe --output symphony.wav --mode melody --format wav
```

#### CLI Options

- `--input, -i`: Input binary file (required)
- `--output, -o`: Output file path (required)
- `--mode`: Mapping mode - `melody`, `rhythm`, or `spectrum` (default: melody)
- `--format`: Output format - `wav`, `mp3`, `midi`, or `spectrum` (default: wav)
- `--debug`: Enable debug output

#### Examples

```bash
# Convert an executable to a melody in WAV format
binarysymphony -i malware.exe -o output.wav

# Generate MIDI from a document with rhythm mode
binarysymphony -i document.pdf -o music.mid -f midi -m rhythm

# Create MP3 with debug info
binarysymphony -i image.png -o sound.mp3 -f mp3 --debug

# Generate spectrogram visualization
binarysymphony -i program.exe -o analysis.png -f spectrum
```

### Graphical User Interface

Launch the GUI:

```bash
python -m binarysymphony.gui
```

Or if installed:

```bash
binarysymphony-gui
```

The GUI provides:
- File selection dialogs
- Mode and format dropdowns
- Real-time progress tracking
- Interactive controls

## How It Works

BinarySymphony maps each byte (0-255) in the input file to musical parameters:

1. **Byte to Note**: Maps byte values to chromatic scale notes (C, C#, D, etc.)
2. **Octave Calculation**: Determines octave based on byte value ranges
3. **Duration**: Assigns fixed or variable note durations
4. **Waveform Generation**: Creates audio waveforms using sine waves
5. **Export**: Saves in desired format (WAV/MP3/MIDI)

### Mapping Modes

- **Melody**: Sequential note playback with fixed duration
- **Rhythm**: Variable note durations for rhythmic patterns
- **Spectrum**: Shorter notes optimized for frequency analysis

## Examples

### Converting a Simple Text File

```bash
echo "Hello World" > hello.txt
binarysymphony -i hello.txt -o hello.wav
```

### Visualizing Binary Structure

```bash
binarysymphony -i program.exe -o analysis.png -m spectrum
```

## API Usage

```python
from binarysymphony import BinaryMapper, MidiExporter, AudioExporter

# Read binary data
with open('file.bin', 'rb') as f:
    data = f.read()

# Map to notes
mapper = BinaryMapper(mode='melody')
notes = mapper.map_bytes_to_notes(data)

# Export as MIDI
midi_exporter = MidiExporter()
midi_exporter.notes_to_midi(notes, 'output.mid')

# Or as WAV
waveform = mapper.generate_waveform(notes)
audio_exporter = AudioExporter()
audio_exporter.save_wav(waveform, 44100, 'output.wav')
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/binarysymphony
flake8 src/binarysymphony
```

### Building for PyPI

```bash
python -m build
twine upload dist/*
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Roadmap

- [ ] AI-powered musical mapping optimization
- [ ] Malware classification-based music profiles
- [ ] Web interface with WebAudio API
- [ ] REST API for binary-to-music conversion
- [ ] Support for additional audio formats
- [ ] Real-time audio streaming

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Inspired by the concept of sonification and data visualization through sound.