import pytest

from codehere.converter import Converter
from codehere.exceptions import NoOpenTagError, UnclosedTagError


class TestTagDetection:
    def test_begin_sep(self):
        c = Converter()
        assert c.is_begin_sep('"""<codehere>"""')
        assert c.is_begin_sep('    """<codehere>"""')
        assert c.is_begin_sep('\t"""<codehere>"""')
        assert not c.is_begin_sep("some code")

    def test_end_sep(self):
        c = Converter()
        assert c.is_end_sep('"""</codehere>"""')
        assert not c.is_end_sep('"""<codehere>"""')

    def test_is_sep(self):
        c = Converter()
        assert c.is_sep('"""<codehere>"""')
        assert c.is_sep('"""</codehere>"""')
        assert not c.is_sep("plain line")


class TestConsistency:
    def test_balanced_tags(self):
        c = Converter()
        lines = ['"""<codehere>"""', "code", '"""</codehere>"""']
        c.check_separators_consistency(lines)  # should not raise

    def test_unclosed_tag(self):
        c = Converter()
        lines = ['"""<codehere>"""', "code"]
        with pytest.raises(UnclosedTagError):
            c.check_separators_consistency(lines)

    def test_no_open_tag(self):
        c = Converter()
        lines = ["code", '"""</codehere>"""']
        with pytest.raises(NoOpenTagError):
            c.check_separators_consistency(lines)

    def test_nested_tags(self):
        c = Converter()
        lines = ['"""<codehere>"""', '"""<codehere>"""', '"""</codehere>"""', '"""</codehere>"""']
        with pytest.raises(UnclosedTagError):
            c.check_separators_consistency(lines)


class TestRenderTextBlock:
    def test_task_mode(self):
        c = Converter()
        lines = ["before\n", '"""<codehere>"""\n', "secret\n", '"""</codehere>"""\n', "after\n"]
        result = c.render_text_block(lines, begin_rep="# BEGIN", end_rep="# END")
        assert "secret\n" not in result
        assert any("raise NotImplementedError" in line for line in result)

    def test_solution_mode(self):
        c = Converter(code_replacement=None)
        lines = ["before\n", '"""<codehere>"""\n', "secret\n", '"""</codehere>"""\n', "after\n"]
        result = c.render_text_block(lines, begin_rep="# BEGIN", end_rep="# END")
        assert "secret\n" in result

    def test_no_tags(self):
        c = Converter()
        lines = ["line1\n", "line2\n"]
        result = c.render_text_block(lines, begin_rep="", end_rep="")
        assert result == lines

    def test_does_not_mutate_input(self):
        c = Converter()
        lines = ["before\n", '"""<codehere>"""\n', "secret\n", '"""</codehere>"""\n']
        original = list(lines)
        c.render_text_block(lines, begin_rep="", end_rep="")
        assert lines == original


class TestProcessLines:
    def test_task_strips_both_tags(self):
        lines = [
            '"""<codehere>"""\n',
            "code\n",
            '"""</codehere>"""\n',
            '"""<comment>"""\n',
            "# grading\n",
            '"""</comment>"""\n',
        ]
        result = Converter().process_lines(lines, solution=False)
        assert not any("<codehere>" in line for line in result)
        assert not any("<comment>" in line for line in result)
        assert not any("# grading" in line for line in result)

    def test_solution_keeps_code(self):
        lines = [
            '"""<codehere>"""\n',
            "code\n",
            '"""</codehere>"""\n',
        ]
        result = Converter().process_lines(lines, solution=True)
        assert "code\n" in result


class TestGetReplacement:
    def test_default(self):
        rep = Converter.get_replacement(inner_string=" Test ")
        assert "Test" in rep
        assert rep.startswith("#")

    def test_empty(self):
        rep = Converter.get_replacement(inner_string="")
        assert rep == "#" * 30
