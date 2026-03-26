# Codehere

Codehere is a tool to prepare your Jupyter notebooks, Python files, and Markdown for seminars and homework.

It takes annotated source files and produces two versions:
- **Task** — student code replaced with `raise NotImplementedError`
- **Solution** — full code kept, annotation tags stripped

## Installation

Install as a CLI tool with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install git+https://github.com/Tviskaron/codehere.git
```

After installation the `codehere` command is available globally:

```bash
codehere homework.ipynb              # generate task version
codehere homework.ipynb --solution   # generate solution version
```

Or with pip:

```bash
pip install git+https://github.com/Tviskaron/codehere.git
```

## Notebook example

A typical workflow: you write a single notebook with slides, exercises, and a compilation cell. Codehere produces clean task and solution versions — the compilation cell removes itself automatically.

**Your source notebook (`seminar.ipynb`):**

| Cell | Type | Content |
|------|------|---------|
| 1 | Markdown | `# Seminar 3: Sorting` |
| 2 | Code | Lecture examples, imports |
| 3 | Code | Exercise with `<codehere>` tags (see below) |
| 4 | Code | Tests wrapped in `<comment>` tags — auto-removed |
| 5 | Code | Compilation cell wrapped in `<comment>` tags — auto-removed |

**Cell 3** — exercise with solution inside:
```python
def merge_sort(arr):
    """<codehere>"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))
    """</codehere>"""
```

**Cell 4** — grading tests (removed from both outputs):
```python
"""<comment>"""
assert merge_sort([3, 1, 2]) == [1, 2, 3]
assert merge_sort([]) == []
"""</comment>"""
```

**Cell 5** — compilation cell at the end of the notebook (removes itself from output):
```python
"""<comment>"""
from codehere import convert
import os

os.makedirs("render", exist_ok=True)
convert(clear=True, outfile="render/task.ipynb")
convert(clear=True, solution=True, outfile="render/solution.ipynb")
"""</comment>"""
```

Run this cell and you get:
- `render/task.ipynb` — `merge_sort` body replaced with `raise NotImplementedError`, cells 4 & 5 gone
- `render/solution.ipynb` — full `merge_sort` code, cells 4 & 5 gone

See a complete working example in [`examples/seminar.ipynb`](examples/seminar.ipynb).

## Tags

Two tag types, both use triple-quoted strings so they are valid Python:

- **`"""<codehere>"""`** / **`"""</codehere>"""`** — wraps student code. In task mode: replaced with `raise NotImplementedError`. In solution mode: tags stripped, code kept.
- **`"""<comment>"""`** / **`"""</comment>"""`** — wraps instructor-only blocks (grading cells, compilation cells). Removed entirely from both outputs.

## CLI usage

```bash
# Generate task version (default)
codehere homework.ipynb

# Generate solution version
codehere homework.ipynb --solution

# Specify output file and clear notebook outputs
codehere homework.ipynb --outfile task.ipynb --clear

# Custom replacement text
codehere homework.py --replacement " TODO "
```

Supported file types: `.py`, `.ipynb`, `.md`

## Python API

```python
from codehere import convert

convert(file="homework.ipynb", outfile="task.ipynb", clear=True)
convert(file="homework.ipynb", outfile="solution.ipynb", solution=True, clear=True)
```

## Development

```bash
uv sync              # Install project + dev deps
uv run pytest        # Run tests
uv run ruff check .  # Lint
```
