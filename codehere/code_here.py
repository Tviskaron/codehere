# !/usr/bin/env python3
import re
import json
import argparse
from copy import deepcopy


class FileRender:
    SEP_TEMPLATE = r'^[\s\t]*{0}[\s\t]*$'

    SEP_BEGIN = '"""<codehere>"""'
    SEP_END = '"""</codehere>"""'

    COMMENT_BEGIN = '"""<comment>"""'
    COMMENT_END = '"""</comment>"""'

    CODE_REPLACEMENT = "raise NotImplementedError"

    def __init__(self, sep_begin=SEP_BEGIN, sep_end=SEP_END, code_replacement=CODE_REPLACEMENT):
        self.begin_sep = sep_begin
        self.end_sep = sep_end
        self.code_replacement = code_replacement

    def check_separators_consistency(self, lines):
        unclosed_begin_separators = 0
        for line in lines:
            if self.is_begin_sep(line) and self.is_end_sep(line):
                raise KeyError('two separators in same line')

            if self.is_begin_sep(line):
                unclosed_begin_separators += 1
            if self.is_end_sep(line):
                unclosed_begin_separators -= 1

            # TODO show lines where error appear
            if unclosed_begin_separators not in (0, 1):
                return False

        if unclosed_begin_separators != 0:
            raise KeyError("latest scope did not closed")

    def get_code_replacement(self):
        return self.code_replacement

    def get_begin_sep(self):
        return self.begin_sep

    def get_end_sep(self):
        return self.end_sep

    def is_begin_sep(self, line):
        return re.search(self.SEP_TEMPLATE.format(self.begin_sep), line)

    def is_end_sep(self, line):
        return re.search(self.SEP_TEMPLATE.format(self.end_sep), line)

    def is_sep(self, line):
        return self.is_begin_sep(line) or self.is_end_sep(line)

    def get_separators_indexes(self, lines):
        self.check_separators_consistency(lines)
        return [index for index, line in enumerate(lines) if self.is_sep(line)]

    def render_text_block(self, lines, begin_rep="#" * 6 + "# Здесь ваш код " + "#" * 10, end_rep="##" + "#" * 30):
    # def render_text_block(self, lines, begin_rep="#" * 6 + " Your code here " + "#" * 10, end_rep="##" + "#" * 30):
        # TODO fix encodings
        lines = deepcopy(lines)
        rev_sep_indexes = list(reversed(self.get_separators_indexes(lines)))
        if not rev_sep_indexes:
            return lines
        for begin, end in zip(rev_sep_indexes[1::2], rev_sep_indexes[::2]):
            if self.code_replacement is None:
                middle = [lines[begin].replace(self.get_begin_sep(), begin_rep),
                          *lines[begin+1:end],
                          lines[end].replace(self.get_end_sep(), end_rep)]
            else:
                middle = [lines[begin].replace(self.get_begin_sep(), begin_rep),
                          lines[begin].replace(self.get_begin_sep(), self.get_code_replacement()),
                          lines[end].replace(self.get_end_sep(), end_rep)]
            lines = lines[:begin] + middle + lines[end + 1:]
        return lines


def get_out_file_name(args):
    if args.outfile:
        return args.outfile
    else:
        filename, extension = args.file
        return filename + "(task)." + extension


def main():
    parser = argparse.ArgumentParser(description="""
                                        Jupiter notebooks and py files compiler for seminars and students homework. 
                                        
                                        Replaces lines with {0} and {1} separators with 
                                        raise NotImplementedError code inside. 
                                     """.format(FileRender().get_begin_sep(), FileRender().get_end_sep()))
    parser.add_argument('file', type=str, help='path to input file')
    parser.add_argument('--outfile', type=str, help='path to output file')
    parser.add_argument('--clear', action='store_true', help='clear code cells outputs')
    parser.add_argument('--solution', action='store_true', help="solution instead of 'NotImplemented'")

    args = parser.parse_args()
    if args.file.endswith(".py"):
        with open(args.file, "r") as in_:
            lines = in_.readlines()
            if args.solution:
                rendered_block = FileRender(code_replacement=None).render_text_block(lines)
            else:
                rendered_block = FileRender().render_text_block(lines)
            rendered_block = FileRender(sep_begin=FileRender.COMMENT_BEGIN,
                                                sep_end=FileRender.COMMENT_END,
                                                code_replacement="").render_text_block(rendered_block,
                                                                                       begin_rep="",
                                                                                       end_rep="")
            with open(get_out_file_name(args), "w") as out:
                out.writelines(rendered_block)

    elif args.file.endswith(".ipynb"):
        with open(args.file, "r") as in_:
            notebook_text = json.load(in_)
            cells = notebook_text['cells']

            for cell in cells:
                if cell['cell_type'] == 'code':
                    if args.solution:
                        cell['source'] = FileRender(code_replacement=None).render_text_block(cell['source'])
                    else:
                        cell['source'] = FileRender().render_text_block(cell['source'])
                    cell['source'] = FileRender(sep_begin=FileRender.COMMENT_BEGIN,
                                                sep_end=FileRender.COMMENT_END,
                                                code_replacement="").render_text_block(cell['source'],
                                                                                       begin_rep="",
                                                                                       end_rep="")
                    if args.clear:
                        cell["outputs"] = []

            with open(get_out_file_name(args), "w") as out:
                json.dump(notebook_text, out, ensure_ascii=False)
    else:
        parser.error("Unrecognized extension of " + args.file)


if __name__ == '__main__':
    main()
