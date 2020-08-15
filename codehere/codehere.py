# !/usr/bin/env python3
import argparse
import json
import os
import pathlib
import re
from argparse import Namespace
from collections import deque
from copy import deepcopy
from re import Match
from typing import List, Optional
from urllib.request import urlopen

import ipykernel
from notebook import notebookapp


class TagError(Exception):
    def __init__(self, message=None):
        self.message = message


class UnclosedTagError(TagError):
    def __init__(self, message=None):
        self.message = message


class NoOpenTagError(TagError):
    def __init__(self, message=None):
        self.message = message


class UnsupportedExtensionError(Exception):
    def __init__(self, message=None):
        self.message = message


class Converter:
    SEP_TEMPLATE = r'^[\s\t]*{0}[;\s\t]*$'

    SEP_BEGIN = '"""<codehere>"""'
    SEP_END = '"""</codehere>"""'

    COMMENT_BEGIN = '"""<comment>"""'
    COMMENT_END = '"""</comment>"""'

    CODE_REPLACEMENT = "raise NotImplementedError"

    def __init__(self, sep_begin: str = SEP_BEGIN, sep_end: str = SEP_END,
                 code_replacement: Optional[str] = CODE_REPLACEMENT) -> None:
        self.begin_sep = sep_begin
        self.end_sep = sep_end
        self.code_replacement = code_replacement

    def check_separators_consistency(self, lines: List[str]) -> None:
        stack = deque()
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

    def get_code_replacement(self) -> Optional[str]:
        return self.code_replacement

    def get_begin_sep(self) -> str:
        return self.begin_sep

    def get_end_sep(self) -> str:
        return self.end_sep

    def is_begin_sep(self, line: str) -> Optional[Match]:
        return re.search(self.SEP_TEMPLATE.format(self.begin_sep), line)

    def is_end_sep(self, line: str) -> Optional[Match]:
        return re.search(self.SEP_TEMPLATE.format(self.end_sep), line)

    def is_sep(self, line: str) -> Optional[Match]:
        return self.is_begin_sep(line) or self.is_end_sep(line)

    def get_separators_indexes(self, lines: List[str]) -> List[int]:
        self.check_separators_consistency(lines)
        return [index for index, line in enumerate(lines) if self.is_sep(line)]

    def render_text_block(self, lines: List[str], begin_rep, end_rep) -> List[str]:
        lines = deepcopy(lines)
        rev_sep_indexes = list(reversed(self.get_separators_indexes(lines)))
        if not rev_sep_indexes:
            return lines
        for begin, end in zip(rev_sep_indexes[1::2], rev_sep_indexes[::2]):
            if self.code_replacement is None:
                middle = [lines[begin].replace(self.get_begin_sep(), begin_rep), *lines[begin + 1:end],
                          lines[end].replace(self.get_end_sep(), end_rep)]
            else:
                middle = [lines[begin].replace(self.get_begin_sep(), begin_rep),
                          lines[begin].replace(self.get_begin_sep(), self.get_code_replacement() or ""),
                          lines[end].replace(self.get_end_sep(), end_rep)]
            lines = lines[:begin] + middle + lines[end + 1:]
        return lines

    @staticmethod
    def get_replacement(inner_string, desired_size=30, symbol='#'):
        left_size = max(0, desired_size - len(inner_string)) // 2
        right_size = max(0, desired_size - left_size - len(inner_string))

        return symbol * left_size + inner_string + symbol * right_size


def get_outfile_name(args: Namespace) -> str:
    filename, extension = os.path.splitext(args.file)
    attempts = 100
    suffix = "-solution" if args.solution else "-task"
    for number in ["", *map(str, range(1, attempts))]:
        result = filename + suffix + number + extension
        if not os.path.exists(result):
            return result
    raise FileExistsError("Cannot get unique outfile name in " + str(attempts) + " attempts")


def parse_arguments():
    parser = argparse.ArgumentParser(description="""
                                            Jupiter notebooks and py files compiler for seminars and students homework. 

                                            Replaces lines with {0} and {1} separators with 
                                            raise NotImplementedError code inside. 
                                         """.format(Converter().get_begin_sep(), Converter().get_end_sep()))
    parser.add_argument('file', type=str, help='path to input file')
    parser.add_argument('--outfile', type=str, help='path to output file')
    parser.add_argument('--clear', action='store_true', help='clear code cells outputs')
    parser.add_argument('--solution', action='store_true', help="solution instead of 'NotImplemented'")
    parser.add_argument('--replacement', action='store_true', help="Replacement for 'Your code here'")

    return parser.parse_args()


def process_py_file(args):
    begin_rep = Converter.get_replacement(inner_string=args.replacement)
    end_rep = Converter.get_replacement(inner_string="")
    with open(args.file, "r") as in_:
        lines = in_.readlines()

        if args.solution:
            rendered_block = Converter(code_replacement=None). \
                render_text_block(lines, begin_rep=begin_rep,
                                  end_rep=end_rep)
        else:
            rendered_block = Converter().render_text_block(lines, begin_rep=begin_rep, end_rep=end_rep)
        rendered_block = Converter(sep_begin=Converter.COMMENT_BEGIN,
                                   sep_end=Converter.COMMENT_END,
                                   code_replacement="").render_text_block(rendered_block,
                                                                          begin_rep="",
                                                                          end_rep="")

        with open(args.outfile, "w") as out:
            out.writelines(rendered_block)


def process_notebook(args):
    begin_rep = Converter.get_replacement(inner_string=args.replacement)
    end_rep = Converter.get_replacement(inner_string="")
    with open(args.file, "r") as in_:
        notebook_text = json.load(in_)
        cells = notebook_text['cells']

        for cell_index, cell in enumerate(cells):
            if cell['cell_type'] == 'code':
                try:
                    if args.solution:
                        cell['source'] = Converter(code_replacement=None). \
                            render_text_block(cell['source'],
                                              begin_rep=begin_rep,
                                              end_rep=end_rep)
                    else:
                        cell['source'] = Converter(). \
                            render_text_block(cell['source'], begin_rep=begin_rep, end_rep=end_rep)
                    cell['source'] = Converter(sep_begin=Converter.COMMENT_BEGIN,
                                               sep_end=Converter.COMMENT_END,
                                               code_replacement=""). \
                        render_text_block(cell['source'],
                                          begin_rep="",
                                          end_rep="")
                    if args.clear:
                        cell["outputs"] = []
                except TagError as tag_error:
                    raise type(tag_error)(tag_error.message + ' in cell: ' + str(cell_index)) from tag_error

        with open(args.outfile, "w") as out:
            json.dump(notebook_text, out, ensure_ascii=False)


def notebook_path():
    """
    From:
    https://stackoverflow.com/questions/12544056/how-do-i-get-the-current-ipython-jupyter-notebook-name/52187331#52187331
    Returns the absolute path of the Notebook or None if it cannot be determined
    NOTE: works only when the security is token-based or there is also no password
    """
    connection_file = os.path.basename(ipykernel.get_connection_file())
    kernel_id = connection_file.split('-', 1)[1].split('.')[0]

    for srv in notebookapp.list_running_servers():
        try:
            if srv['token'] == '' and not srv['password']:  # No token and no password, ahem...
                req = urlopen(srv['url'] + 'api/sessions')
            else:
                req = urlopen(srv['url'] + 'api/sessions?token=' + srv['token'])
            sessions = json.load(req)
            for sess in sessions:
                if sess['kernel']['id'] == kernel_id:
                    return os.path.join(srv['notebook_dir'], sess['notebook']['path'])
        except:
            pass  # There may be stale entries in the runtime directory
    return None


def process(args: Optional[Namespace] = None) -> None:
    if args is None:
        args = parse_arguments()
    if args.file is None:
        nb_path = notebook_path()
        if nb_path:
            args.file = nb_path
        else:
            raise FileNotFoundError("Cannot determine input file location. Please specify it directly.")
    if args.outfile is None:
        args.outfile = get_outfile_name(args)

    if args.file.endswith(".py"):
        process_py_file(args)
    elif args.file.endswith(".ipynb"):
        process_notebook(args)
    else:
        raise UnsupportedExtensionError("File with unrecognized extension: " + args.file + " \n" +
                                        'Codehere supports only "*.ipynb" and "*.py" files.')
    print("Saved in: ", args.outfile)


def convert(file: Optional[str] = None, outfile: Optional[str] = None, solution: bool = False, clear: bool = False,
            replacement=" Your code here ") -> None:
    process(Namespace(**{
        "file": file,
        "outfile": outfile,
        "solution": solution,
        "clear": clear,
        "replacement": replacement
    }))


if __name__ == '__main__':
    process()
