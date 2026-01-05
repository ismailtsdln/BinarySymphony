"""Command-line interface for BinarySymphony."""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.text import Text

from .core import BinaryMapper
from .midi_export import MidiExporter
from .audio_export import AudioExporter
from .visualization import Visualizer

console = Console()


def validate_file(file_path: str) -> Path:
    """Validate input file exists and is readable."""
    path = Path(file_path)
    if not path.exists():
        console.print(f"[red]❌ Error:[/red] File '{file_path}' does not exist.")
        raise FileNotFoundError(f"File {file_path} does not exist.")
    if not path.is_file():
        console.print(f"[red]❌ Error:[/red] '{file_path}' is not a regular file.")
        raise ValueError(f"{file_path} is not a file.")
    return path


def main():
    # ASCII Art Header
    header = Text("🎵 BinarySymphony 🎵", style="bold magenta")
    console.print(Panel(header, title="Welcome", border_style="blue"))

    parser = argparse.ArgumentParser(
        description="Convert binary files to musical symphonies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  binarysymphony -i file.exe -o music.wav
  binarysymphony -i data.bin -o output.mid -f midi -m rhythm
  binarysymphony -i program.bin -o spectrum.png -f spectrum --debug
        """
    )
    parser.add_argument("--input", "-i", required=True, help="Input binary file")
    parser.add_argument("--output", "-o", required=True, help="Output file")
    parser.add_argument(
        "--mode",
        choices=["melody", "rhythm", "spectrum"],
        default="melody",
        help="Mapping mode (default: melody)",
    )
    parser.add_argument(
        "--format", choices=["wav", "mp3", "midi", "spectrum"], default="wav", help="Output format (default: wav)"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    try:
        # Validate input file
        console.print(f"[cyan]📁[/cyan] Validating input file: {args.input}")
        input_path = validate_file(args.input)

        # Show file info
        file_size = input_path.stat().st_size
        console.print(f"[green]✅[/green] File validated: {file_size} bytes")

        # Show configuration
        config_panel = Panel(
            f"Mode: [bold cyan]{args.mode}[/bold cyan]\n"
            f"Format: [bold cyan]{args.format}[/bold cyan]\n"
            f"Output: [bold cyan]{args.output}[/bold cyan]",
            title="Configuration",
            border_style="green"
        )
        console.print(config_panel)

        # Progress bar setup
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Processing...", total=100)

            # Read binary data
            progress.update(task, description="Reading binary data...", completed=10)
            with open(input_path, "rb") as f:
                data = f.read()

            if not data:
                progress.update(task, completed=100)
                error_panel = Panel(
                    "[red]❌ Input file is empty[/red]",
                    title="Error",
                    border_style="red"
                )
                console.print(error_panel)
                sys.exit(1)

            progress.update(task, completed=30)

            if args.debug:
                console.print(f"[dim]🔍 Debug: Read {len(data)} bytes[/dim]")

            # Map to notes
            progress.update(task, description="Mapping bytes to notes...", completed=50)
            mapper = BinaryMapper(mode=args.mode)
            notes = mapper.map_bytes_to_notes(data)

            progress.update(task, completed=70)

            if args.debug:
                console.print(f"[dim]🔍 Debug: Generated {len(notes)} notes[/dim]")

            # Export based on format
            progress.update(task, description=f"Exporting to {args.format.upper()}...", completed=90)

            if args.format == "midi":
                exporter = MidiExporter()
                exporter.notes_to_midi(notes, str(Path(args.output)))
            elif args.format in ["wav", "mp3"]:
                waveform = mapper.generate_waveform(notes)
                exporter = AudioExporter()
                if args.format == "wav":
                    exporter.save_wav(waveform, 44100, str(Path(args.output)))
                else:
                    exporter.save_mp3(waveform, 44100, str(Path(args.output)))
            elif args.format == "spectrum":
                waveform = mapper.generate_waveform(notes)
                visualizer = Visualizer()
                visualizer.plot_spectrogram(waveform, 44100, str(Path(args.output)))

            progress.update(task, completed=100)

        # Success message
        success_panel = Panel(
            f"🎉 [bold green]Success![/bold green]\n"
            f"Output saved to: [bold cyan]{args.output}[/bold cyan]\n"
            f"Generated {len(notes)} musical notes from {len(data)} bytes",
            title="Complete",
            border_style="green"
        )
        console.print(success_panel)

    except Exception as e:
        error_panel = Panel(
            f"[red]❌ An error occurred:[/red]\n{str(e)}",
            title="Error",
            border_style="red"
        )
        console.print(error_panel)
        if args.debug:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
