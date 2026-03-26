import json

import pytest

from codehere.exceptions import UnsupportedExtensionError
from codehere.processors import process_file, process_markdown, process_notebook, process_py


class TestProcessPy:
    def test_task(self, sample_py, tmp_path):
        out = str(tmp_path / "out.py")
        process_py(sample_py, out)
        text = open(out).read()
        assert "raise NotImplementedError" in text
        assert "math.pi * radius ** 2" not in text
        assert "grading" not in text

    def test_solution(self, sample_py, tmp_path):
        out = str(tmp_path / "out.py")
        process_py(sample_py, out, solution=True)
        text = open(out).read()
        assert "math.pi * radius ** 2" in text
        assert "raise NotImplementedError" not in text
        assert "grading" not in text


class TestProcessNotebook:
    def test_task(self, sample_ipynb, tmp_path):
        out = str(tmp_path / "out.ipynb")
        process_notebook(sample_ipynb, out)
        nb = json.loads(open(out).read())
        code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
        first_source = "".join(code_cells[0]["source"])
        assert "raise NotImplementedError" in first_source
        assert "math.sqrt(2)" not in first_source

    def test_solution(self, sample_ipynb, tmp_path):
        out = str(tmp_path / "out.ipynb")
        process_notebook(sample_ipynb, out, solution=True)
        nb = json.loads(open(out).read())
        code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
        first_source = "".join(code_cells[0]["source"])
        assert "math.sqrt(2)" in first_source

    def test_clear_outputs(self, sample_ipynb, tmp_path):
        out = str(tmp_path / "out.ipynb")
        process_notebook(sample_ipynb, out, clear=True)
        nb = json.loads(open(out).read())
        code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
        for cell in code_cells:
            assert cell["outputs"] == []

    def test_comment_tags_removed(self, sample_ipynb, tmp_path):
        out = str(tmp_path / "out.ipynb")
        process_notebook(sample_ipynb, out)
        nb = json.loads(open(out).read())
        code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
        second_source = "".join(code_cells[1]["source"])
        assert "grading" not in second_source


class TestProcessMarkdown:
    def test_task(self, sample_md, tmp_path):
        out = str(tmp_path / "out.md")
        process_markdown(sample_md, out)
        text = open(out).read()
        assert "raise NotImplementedError" in text
        assert "return 42" not in text
        assert "Expected output" not in text

    def test_solution(self, sample_md, tmp_path):
        out = str(tmp_path / "out.md")
        process_markdown(sample_md, out, solution=True)
        text = open(out).read()
        assert "return 42" in text
        assert "Expected output" not in text


class TestProcessFile:
    def test_dispatches_py(self, sample_py, tmp_path):
        out = str(tmp_path / "out.py")
        process_file(sample_py, out)
        assert "raise NotImplementedError" in open(out).read()

    def test_dispatches_ipynb(self, sample_ipynb, tmp_path):
        out = str(tmp_path / "out.ipynb")
        process_file(sample_ipynb, out)
        assert "raise NotImplementedError" in open(out).read()

    def test_dispatches_md(self, sample_md, tmp_path):
        out = str(tmp_path / "out.md")
        process_file(sample_md, out)
        assert "raise NotImplementedError" in open(out).read()

    def test_unsupported_extension(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        with pytest.raises(UnsupportedExtensionError):
            process_file(str(f), str(tmp_path / "out.txt"))
