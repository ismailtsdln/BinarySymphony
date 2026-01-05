"""Graphical user interface for BinarySymphony."""

import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QComboBox,
    QTextEdit,
    QProgressBar,
)
from PyQt6.QtCore import QThread, pyqtSignal

from .core import BinaryMapper
from .midi_export import MidiExporter
from .audio_export import AudioExporter
from .visualization import Visualizer


class WorkerThread(QThread):
    """Worker thread for processing."""

    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, input_file, mode, output_format, output_file):
        super().__init__()
        self.input_file = input_file
        self.mode = mode
        self.output_format = output_format
        self.output_file = output_file

    def run(self):
        try:
            # Read data
            with open(self.input_file, "rb") as f:
                data = f.read()
            if not data:
                raise ValueError("Input file is empty")
            self.progress.emit(25)

            # Map notes
            mapper = BinaryMapper(mode=self.mode)
            notes = mapper.map_bytes_to_notes(data)
            self.progress.emit(50)

            # Export
            if self.output_format == "midi":
                exporter = MidiExporter()
                exporter.notes_to_midi(notes, self.output_file)
            elif self.output_format in ["wav", "mp3"]:
                waveform = mapper.generate_waveform(notes)
                exporter = AudioExporter()
                if self.output_format == "wav":
                    exporter.save_wav(waveform, 44100, self.output_file)
                else:
                    exporter.save_mp3(waveform, 44100, self.output_file)
            elif self.output_format == "spectrum":
                waveform = mapper.generate_waveform(notes)
                visualizer = Visualizer()
                visualizer.plot_spectrogram(waveform, 44100, self.output_file)
            self.progress.emit(100)
            self.finished.emit(f"Success: Output saved to {self.output_file}")
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")


class BinarySymphonyGUI(QWidget):
    """Main GUI window."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("BinarySymphony")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.select_button = QPushButton("Select Binary File")
        self.select_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.select_button)
        layout.addLayout(file_layout)

        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["melody", "rhythm", "spectrum"])
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["wav", "mp3", "midi", "spectrum"])
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # Output file
        output_layout = QHBoxLayout()
        self.output_label = QLabel("Output: output.wav")
        self.output_button = QPushButton("Select Output")
        self.output_button.clicked.connect(self.select_output)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_button)
        layout.addLayout(output_layout)

        # Progress
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Convert button
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.convert)
        layout.addWidget(self.convert_button)

        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.setLayout(layout)

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Binary File")
        if file_name:
            self.file_label.setText(file_name)
            self.input_file = file_name

    def select_output(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Select Output File")
        if file_name:
            self.output_label.setText(file_name)
            self.output_file = file_name

    def convert(self):
        if not hasattr(self, "input_file"):
            self.log_text.append("Please select an input file.")
            return
        if not hasattr(self, "output_file"):
            self.log_text.append("Please select an output file.")
            return

        self.progress_bar.setValue(0)
        self.worker = WorkerThread(
            self.input_file,
            self.mode_combo.currentText(),
            self.format_combo.currentText(),
            self.output_file,
        )
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, message):
        self.log_text.append(message)


def main():
    app = QApplication(sys.argv)
    gui = BinarySymphonyGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
