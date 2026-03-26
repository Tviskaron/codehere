from pathlib import Path

SUPPORTED_EXTENSIONS = {".py", ".ipynb", ".md"}


def is_supported_file(path: str | Path) -> bool:
    return Path(path).suffix in SUPPORTED_EXTENSIONS


def get_outfile_path(file: str, *, solution: bool = False) -> str:
    p = Path(file)
    suffix = "-solution" if solution else "-task"
    attempts = 100
    for number in ["", *map(str, range(1, attempts))]:
        candidate = p.with_stem(p.stem + suffix + number)
        if not candidate.exists():
            return str(candidate)
    raise FileExistsError("Cannot get unique outfile name in " + str(attempts) + " attempts")
