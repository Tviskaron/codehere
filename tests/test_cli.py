import pytest

from codehere.cli import build_parser, main


class TestBuildParser:
    def test_version_flag(self, capsys):
        parser = build_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "0.2.0" in captured.out

    def test_replacement_is_string(self):
        parser = build_parser()
        args = parser.parse_args(["file.py", "--replacement", "TODO"])
        assert args.replacement == "TODO"

    def test_defaults(self):
        parser = build_parser()
        args = parser.parse_args(["file.py"])
        assert args.file == "file.py"
        assert args.solution is False
        assert args.clear is False
        assert args.outfile is None
        assert args.replacement == " Your code here "


class TestMain:
    def test_missing_file(self, tmp_path):
        with pytest.raises((SystemExit, FileNotFoundError)):
            main(["nonexistent.py"])

    def test_processes_file(self, sample_py, tmp_path):
        out = str(tmp_path / "out.py")
        main([sample_py, "--outfile", out])
        text = open(out).read()
        assert "raise NotImplementedError" in text

    def test_solution_flag(self, sample_py, tmp_path):
        out = str(tmp_path / "out.py")
        main([sample_py, "--outfile", out, "--solution"])
        text = open(out).read()
        assert "math.pi * radius ** 2" in text

    def test_custom_replacement(self, sample_py, tmp_path):
        out = str(tmp_path / "out.py")
        main([sample_py, "--outfile", out, "--replacement", "TODO"])
        text = open(out).read()
        assert "TODO" in text
