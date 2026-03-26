import pytest

from codehere import convert


class TestConvertAPI:
    def test_import_path(self):
        from codehere import convert as convert_fn

        assert callable(convert_fn)

    def test_no_file_raises(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)  # empty dir, no .ipynb to auto-detect
        with pytest.raises(FileNotFoundError):
            convert()

    def test_convert_py(self, sample_py, tmp_path):
        out = str(tmp_path / "out.py")
        convert(file=sample_py, outfile=out)
        text = open(out).read()
        assert "raise NotImplementedError" in text

    def test_convert_solution(self, sample_py, tmp_path):
        out = str(tmp_path / "out.py")
        convert(file=sample_py, outfile=out, solution=True)
        text = open(out).read()
        assert "math.pi * radius ** 2" in text

    def test_convert_custom_replacement(self, sample_py, tmp_path):
        out = str(tmp_path / "out.py")
        convert(file=sample_py, outfile=out, replacement=" TODO ")
        text = open(out).read()
        assert "TODO" in text


class TestPublicExports:
    def test_all_exports(self):
        import codehere

        assert hasattr(codehere, "Converter")
        assert hasattr(codehere, "convert")
        assert hasattr(codehere, "process_file")
        assert hasattr(codehere, "CodehereError")
        assert hasattr(codehere, "TagError")
        assert hasattr(codehere, "UnclosedTagError")
        assert hasattr(codehere, "NoOpenTagError")
        assert hasattr(codehere, "UnsupportedExtensionError")
        assert hasattr(codehere, "__version__")
