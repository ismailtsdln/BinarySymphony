"""Command-line interface for BinarySymphony."""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
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
  # Single file processing
  binarysymphony -i file.exe -o music.wav
  binarysymphony -i data.bin -o output.mid -f midi -m rhythm --scale major

  # Batch processing
  binarysymphony --batch --input-dir ./files --output ./output
  binarysymphony --batch --input-dir /path/to/files -o /path/to/output -f mp3
        """,
    )
    parser.add_argument(
        "--input",
        "-i",
        help="Input binary file (use --batch for multiple files)",
    )
    parser.add_argument("--input-dir", help="Input directory for batch processing")
    parser.add_argument(
        "--output", "-o", required=True, help="Output file or directory"
    )
    parser.add_argument(
        "--mode",
        choices=["melody", "rhythm", "spectrum"],
        default="melody",
        help="Mapping mode (default: melody)",
    )
    parser.add_argument(
        "--scale",
        choices=[
            "chromatic",
            "major",
            "minor",
            "pentatonic",
            "blues",
            "dorian",
            "phrygian",
        ],
        default="chromatic",
        help="Musical scale (default: chromatic)",
    )
    parser.add_argument(
        "--format",
        choices=["wav", "mp3", "midi", "spectrum"],
        default="wav",
        help="Output format (default: wav)",
    )
    parser.add_argument(
        "--batch", action="store_true", help="Enable batch processing mode"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    # Validate arguments
    if args.batch:
        if not args.input_dir:
            console.print(
                "[red]❌ Error:[/red] --input-dir is required when using --batch"
            )
            sys.exit(1)
        if not Path(args.input_dir).is_dir():
            console.print(
                f"[red]❌ Error:[/red] '{args.input_dir}' is not a valid directory"
            )
            sys.exit(1)
    else:
        if not args.input:
            console.print(
                "[red]❌ Error:[/red] --input is required when not using --batch"
            )
            sys.exit(1)

    try:
        # Single file processing mode
        if not args.batch:
            # Validate input file
            console.print(f"[cyan]📁[/cyan] Validating input file: {args.input}")
            input_path = validate_file(args.input)

            # Show file info
            file_size = input_path.stat().st_size
            console.print(f"[green]✅[/green] File validated: {file_size} bytes")

            # Show configuration
            config_panel = Panel(
                f"Mode: [bold cyan]{args.mode}[/bold cyan]\n"
                f"Scale: [bold cyan]{args.scale}[/bold cyan]\n"
                f"Format: [bold cyan]{args.format}[/bold cyan]\n"
                f"Output: [bold cyan]{args.output}[/bold cyan]",
                title="Configuration",
                border_style="green",
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
                progress.update(
                    task, description="Reading binary data...", completed=10
                )
                with open(input_path, "rb") as f:
                    data = f.read()

                if not data:
                    progress.update(task, completed=100)
                    error_panel = Panel(
                        "[red]❌ Input file is empty[/red]",
                        title="Error",
                        border_style="red",
                    )
                    console.print(error_panel)
                    sys.exit(1)

                progress.update(task, completed=30)

                if args.debug:
                    console.print(f"[dim]🔍 Debug: Read {len(data)} bytes[/dim]")

                # Map to notes
                progress.update(
                    task, description="Mapping bytes to notes...", completed=50
                )
                mapper = BinaryMapper(mode=args.mode, scale=args.scale)
                notes = mapper.map_bytes_to_notes(data)

                progress.update(task, completed=70)

                if args.debug:
                    console.print(f"[dim]🔍 Debug: Generated {len(notes)} notes[/dim]")

                # Export based on format
                progress.update(
                    task,
                    description=f"Exporting to {args.format.upper()}...",
                    completed=90,
                )

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
                border_style="green",
            )
            console.print(success_panel)

        # Batch processing mode
        else:
            console.print(f"[cyan]📁[/cyan] Scanning directory: {args.input_dir}")

            # Find all files in directory
            input_dir = Path(args.input_dir)
            input_files = []
            for ext in ["*"]:  # Process all files
                input_files.extend(input_dir.glob(f"**/{ext}"))

            # Filter out directories and hidden files
            input_files = [
                f for f in input_files if f.is_file() and not f.name.startswith(".")
            ]

            if not input_files:
                console.print(
                    "[yellow]⚠️ Warning:[/yellow] No files found in directory"
                )
                return

            console.print(
                f"[green]📋[/green] Found {len(input_files)} files to process"
            )

            # Create output directory if it doesn't exist
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Show batch configuration
            batch_config = Panel(
                f"Input Directory: [bold cyan]{args.input_dir}[/bold cyan]\n"
                f"Output Directory: [bold cyan]{args.output}[/bold cyan]\n"
                f"Files to Process: [bold cyan]{len(input_files)}[/bold cyan]\n"
                f"Mode: [bold cyan]{args.mode}[/bold cyan]\n"
                f"Scale: [bold cyan]{args.scale}[/bold cyan]\n"
                f"Format: [bold cyan]{args.format}[/bold cyan]",
                title="Batch Processing Configuration",
                border_style="blue",
            )
            console.print(batch_config)

            # Initialize mapper
            mapper = BinaryMapper(mode=args.mode, scale=args.scale)

            # Progress tracking
            processed = 0
            successful = 0
            failed = 0

            def progress_callback(current, total, result):
                nonlocal processed, successful, failed
                processed += 1

                if result["status"] == "success":
                    successful += 1
                    status_icon = "✅"
                    status_color = "green"
                else:
                    failed += 1
                    status_icon = "❌"
                    status_color = "red"

                console.print(
                    f"[{status_color}]{status_icon}[/{status_color}] "
                    f"{result['input']} → {result.get('output', 'N/A')}"
                )
                if result.get("error"):
                    console.print(f"   [red]Error: {result['error']}[/red]")

            # Process batch
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                TimeElapsedColumn(),
                console=console,
                transient=False,
            ) as progress:
                task = progress.add_task("Processing files...", total=len(input_files))

                def batch_progress(current, total, result):
                    progress_callback(current, total, result)
                    progress.update(task, completed=current)

                results = mapper.process_batch(
                    input_files=[str(f) for f in input_files],
                    output_dir=str(output_dir),
                    output_format=args.format,
                    progress_callback=batch_progress,
                )

            # Batch summary
            batch_summary = Panel(
                f"📊 [bold green]Batch Processing Complete[/bold green]\n"
                f"Total Files: [bold cyan]{len(results)}[/bold cyan]\n"
                f"Successful: [bold green]{successful}[/bold green]\n"
                f"Failed: [bold red]{failed}[/bold red]\n"
                f"Output Directory: [bold cyan]{args.output}[/bold cyan]",
                title="Batch Summary",
                border_style="green",
            )
            console.print(batch_summary)

    except Exception as e:
        error_panel = Panel(
            f"[red]❌ An error occurred:[/red]\n{str(e)}",
            title="Error",
            border_style="red",
        )
        console.print(error_panel)
        if args.debug:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
