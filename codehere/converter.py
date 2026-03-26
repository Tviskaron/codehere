import re

from codehere.exceptions import NoOpenTagError, UnclosedTagError


class Converter:
    SEP_TEMPLATE = r"^[\s\t]*{0}[;\s\t]*$"

    SEP_BEGIN = '"""<codehere>"""'
    SEP_END = '"""</codehere>"""'

    COMMENT_BEGIN = '"""<comment>"""'
    COMMENT_END = '"""</comment>"""'

    CODE_REPLACEMENT = "raise NotImplementedError"

    def __init__(
        self,
        sep_begin: str = SEP_BEGIN,
        sep_end: str = SEP_END,
        code_replacement: str | None = CODE_REPLACEMENT,
    ) -> None:
        self.begin_sep = sep_begin
        self.end_sep = sep_end
        self.code_replacement = code_replacement

    def check_separators_consistency(self, lines: list[str]) -> None:
        stack: list[int] = []
        for index, line in enumerate(lines):
            if self.is_begin_sep(line):
                stack.append(index)
            if self.is_end_sep(line):
                if len(stack) == 0:
                    raise NoOpenTagError("No open tag for line: " + str(index))
                stack.pop()

            if len(stack) > 1:
                raise UnclosedTagError("Unclosed tag in line: " + str(stack.pop()))

        if len(stack) != 0:
            raise UnclosedTagError("Unclosed tag in line: " + str(stack.pop()))

    def is_begin_sep(self, line: str) -> re.Match | None:
        return re.search(self.SEP_TEMPLATE.format(self.begin_sep), line)

    def is_end_sep(self, line: str) -> re.Match | None:
        return re.search(self.SEP_TEMPLATE.format(self.end_sep), line)

    def is_sep(self, line: str) -> re.Match | None:
        return self.is_begin_sep(line) or self.is_end_sep(line)

    def get_separators_indexes(self, lines: list[str]) -> list[int]:
        self.check_separators_consistency(lines)
        return [index for index, line in enumerate(lines) if self.is_sep(line)]

    def render_text_block(self, lines: list[str], begin_rep: str, end_rep: str) -> list[str]:
        lines = list(lines)
        rev_sep_indexes = list(reversed(self.get_separators_indexes(lines)))
        if not rev_sep_indexes:
            return lines
        for begin, end in zip(rev_sep_indexes[1::2], rev_sep_indexes[::2]):
            if self.code_replacement is None:
                middle = [
                    lines[begin].replace(self.begin_sep, begin_rep),
                    *lines[begin + 1 : end],
                    lines[end].replace(self.end_sep, end_rep),
                ]
            else:
                middle = [
                    lines[begin].replace(self.begin_sep, begin_rep),
                    lines[begin].replace(self.begin_sep, self.code_replacement),
                    lines[end].replace(self.end_sep, end_rep),
                ]
            lines = lines[:begin] + middle + lines[end + 1 :]
        return lines

    def process_lines(self, lines: list[str], *, solution: bool = False, replacement: str = " Your code here ") -> list[str]:
        """Run both codehere and comment tag passes on *lines*."""
        begin_rep = self.get_replacement(inner_string=replacement)
        end_rep = self.get_replacement(inner_string="")

        codehere_converter = Converter(code_replacement=None) if solution else Converter()
        result = codehere_converter.render_text_block(lines, begin_rep=begin_rep, end_rep=end_rep)

        comment_converter = Converter(
            sep_begin=self.COMMENT_BEGIN,
            sep_end=self.COMMENT_END,
            code_replacement="",
        )
        return comment_converter.render_text_block(result, begin_rep="", end_rep="")

    @staticmethod
    def get_replacement(inner_string: str, desired_size: int = 30, symbol: str = "#") -> str:
        left_size = max(0, desired_size - len(inner_string)) // 2
        right_size = max(0, desired_size - left_size - len(inner_string))
        return symbol * left_size + inner_string + symbol * right_size
