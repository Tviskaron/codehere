"""Codehere — prepare annotated code for teaching."""

__version__ = "0.2.0"

from codehere.converter import Converter
from codehere.exceptions import (
    CodehereError,
    NoOpenTagError,
    TagError,
    UnclosedTagError,
    UnsupportedExtensionError,
)
from codehere.processors import process_file
from codehere.utils import get_outfile_path


def convert(
    file: str | None = None,
    outfile: str | None = None,
    solution: bool = False,
    clear: bool = False,
    replacement: str = " Your code here ",
) -> None:
    """Backward-compatible entry point."""
    if file is None:
        raise FileNotFoundError("Cannot determine input file location. Please specify it directly.")
    if outfile is None:
        outfile = get_outfile_path(file, solution=solution)
    process_file(file, outfile, solution=solution, clear=clear, replacement=replacement)
    print("Saved in:", outfile)


__all__ = [
    "Converter",
    "CodehereError",
    "NoOpenTagError",
    "TagError",
    "UnclosedTagError",
    "UnsupportedExtensionError",
    "convert",
    "get_outfile_path",
    "process_file",
]
