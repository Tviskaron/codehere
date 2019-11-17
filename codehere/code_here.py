# !/usr/bin/env python3
import re
import json
import argparse
import os
from copy import deepcopy


class FileRender:
    _SEP_BEGIN = '"""<code>"""'
    _SEP_END = '"""</code>"""'
    _CODE_REPLACEMENT = "raise NotImplementedError"
    _SEP_TEMPLATE = r'^[\s\t]*{0}[\s\t]*$'

    @classmethod
    def check_separators_consistency(cls, lines):
        unclosed_begin_separators = 0
        for line in lines:
            if cls.is_begin_sep(line) and cls.is_end_sep(line):
                raise KeyError('two separators in same line')

            if cls.is_begin_sep(line):
                unclosed_begin_separators += 1
            if cls.is_end_sep(line):
                unclosed_begin_separators -= 1

            # TODO show lines where error appear
            if unclosed_begin_separators not in (0, 1):
                return False

        if unclosed_begin_separators != 0:
            raise KeyError("latest scope did not closed")

    @classmethod
    def get_code_replacement(cls):
        return cls._CODE_REPLACEMENT

    @classmethod
    def get_begin_sep(cls):
        return cls._SEP_BEGIN

    @classmethod
    def get_end_sep(cls):
        return cls._SEP_END

    @classmethod
    def is_begin_sep(cls, line):
        return re.search(cls._SEP_TEMPLATE.format(cls._SEP_BEGIN), line)

    @classmethod
    def is_end_sep(cls, line):
        return re.search(cls._SEP_TEMPLATE.format(cls._SEP_END), line)

    @classmethod
    def is_sep(cls, line):
        return cls.is_begin_sep(line) or cls.is_end_sep(line)

    @classmethod
    def get_separators_indexes(cls, lines):
        cls.check_separators_consistency(lines)
        return [index for index, line in enumerate(lines) if cls.is_sep(line)]

    def render_text_block(self, lines, begin_rep="#" * 6 + " Your code here " + "#" * 10, end_rep="##" + "#" * 30):
        lines = deepcopy(lines)

        rev_sep_indexes = list(reversed(self.get_separators_indexes(lines)))
        if not rev_sep_indexes:
            return lines

        for begin, end in zip(rev_sep_indexes[1::2], rev_sep_indexes[::2]):
            middle = [lines[begin].replace(self.get_begin_sep(), begin_rep),
                      lines[begin].replace(self.get_begin_sep(), self.get_code_replacement()),
                      lines[end].replace(self.get_end_sep(), end_rep)]
            lines = lines[:begin] + middle + lines[end + 1:]
        return lines


def get_out_file_name(file):
    # todo rewrite with proper settings
    # return "out.py"
    return file.split(".")[0] + "(task)." + file.split(".")[1]


def main():
    parser = argparse.ArgumentParser(description="""
                                        Jupiter notebooks and py files compiler for seminars and students homework. 
                                        
                                        Replaces lines with {0} and {1} separators with 
                                        raise NotImplementedError code inside. 
                                     """.format(FileRender.get_begin_sep(), FileRender.get_end_sep()))
    parser.add_argument('file', type=str, help='path to input file')
    args = parser.parse_args()

    if args.file.endswith(".py"):
        with open(args.file, "r") as in_:
            lines = in_.readlines()
            rendered_block = FileRender().render_text_block(lines)
            with open(get_out_file_name(args.file), "w") as out:
                out.writelines(rendered_block)

    elif args.file.endswith(".ipynb"):
        with open(args.file, "r") as in_:
            notebook_text = json.load(in_)
            cells = notebook_text['cells']

            for cell in cells:
                if cell['cell_type'] == 'code':
                    cell['source'] = FileRender().render_text_block(cell['source'])
            with open(get_out_file_name(args.file), "w") as out:
                json.dump(notebook_text, out)
    else:
        parser.error("Unrecognized extension of " + args.file)


if __name__ == '__main__':
    main()
