import argparse
import sys

from codehere.processors import process_file
from codehere.utils import get_outfile_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare Jupyter notebooks, Python files, and Markdown for seminars and homework.",
    )
    parser.add_argument("file", type=str, help="path to input file")
    parser.add_argument("--outfile", type=str, help="path to output file")
    parser.add_argument("--clear", action="store_true", help="clear code cells outputs (notebooks only)")
    parser.add_argument("--solution", action="store_true", help="keep solution code instead of replacing with NotImplementedError")
    parser.add_argument("--replacement", type=str, default=" Your code here ", help="text for the 'your code here' banner")
    parser.add_argument("--version", action="version", version=f"%(prog)s {_get_version()}")
    return parser


def _get_version() -> str:
    from codehere import __version__

    return __version__


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.outfile is None:
        args.outfile = get_outfile_path(args.file, solution=args.solution)

    process_file(
        args.file,
        args.outfile,
        solution=args.solution,
        clear=args.clear,
        replacement=args.replacement,
    )
    print("Saved in:", args.outfile, file=sys.stderr)
