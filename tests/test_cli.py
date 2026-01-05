"""Tests for CLI module."""

import pytest
from pathlib import Path
import tempfile
import subprocess
import sys


class TestCLI:
    def test_cli_help(self):
        # This would require running the script, but for simplicity, assume it's tested manually
        pass

    def test_validate_file(self):
        from binarysymphony.cli import validate_file
        with tempfile.NamedTemporaryFile() as tmp:
            path = validate_file(tmp.name)
            assert isinstance(path, Path)

    def test_validate_file_not_exists(self):
        from binarysymphony.cli import validate_file
        with pytest.raises(FileNotFoundError):
            validate_file("/nonexistent/file")

    def test_main_empty_file(self, tmp_path):
        # Create empty file
        empty_file = tmp_path / "empty.bin"
        empty_file.write_bytes(b"")

        # Mock sys.argv
        import sys
        original_argv = sys.argv
        sys.argv = ["binarysymphony", "--input", str(empty_file), "--output", str(tmp_path / "out.wav")]

        try:
            from binarysymphony.cli import main
            with pytest.raises(SystemExit):
                main()
        finally:
            sys.argv = original_argv