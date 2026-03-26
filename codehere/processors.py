import json

from codehere.converter import Converter
from codehere.exceptions import TagError, UnsupportedExtensionError
from codehere.utils import SUPPORTED_EXTENSIONS


def process_py(
    infile: str,
    outfile: str,
    *,
    solution: bool = False,
    replacement: str = " Your code here ",
) -> None:
    with open(infile) as f:
        lines = f.readlines()

    result = Converter().process_lines(lines, solution=solution, replacement=replacement)

    with open(outfile, "w") as f:
        f.writelines(result)


def process_notebook(
    infile: str,
    outfile: str,
    *,
    solution: bool = False,
    clear: bool = False,
    replacement: str = " Your code here ",
) -> None:
    with open(infile) as f:
        notebook = json.load(f)

    converter = Converter()
    for cell_index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] == "code":
            try:
                cell["source"] = converter.process_lines(cell["source"], solution=solution, replacement=replacement)
                if clear:
                    cell["outputs"] = []
            except TagError as e:
                raise type(e)(
                    (e.message or "") + " in cell: " + str(cell_index),
                    line=e.line,
                    cell=cell_index,
                ) from e

    with open(outfile, "w") as f:
        json.dump(notebook, f, ensure_ascii=False)


def process_markdown(
    infile: str,
    outfile: str,
    *,
    solution: bool = False,
    replacement: str = " Your code here ",
) -> None:
    with open(infile) as f:
        lines = f.readlines()

    result = Converter().process_lines(lines, solution=solution, replacement=replacement)

    with open(outfile, "w") as f:
        f.writelines(result)


def process_file(
    infile: str,
    outfile: str,
    *,
    solution: bool = False,
    clear: bool = False,
    replacement: str = " Your code here ",
) -> None:
    if infile.endswith(".py"):
        process_py(infile, outfile, solution=solution, replacement=replacement)
    elif infile.endswith(".ipynb"):
        process_notebook(infile, outfile, solution=solution, clear=clear, replacement=replacement)
    elif infile.endswith(".md"):
        process_markdown(infile, outfile, solution=solution, replacement=replacement)
    else:
        raise UnsupportedExtensionError(
            f"File with unrecognized extension: {infile}\n"
            f"Codehere supports only {', '.join(sorted(SUPPORTED_EXTENSIONS))} files."
        )
