import codecs
import os
import re

from setuptools import setup, find_packages

cur_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(cur_dir, 'README.md'), 'rb') as f:
    lines = [x.decode('utf-8') for x in f.readlines()]
    lines = ''.join([re.sub('^<.*>\n$', '', x) for x in lines])
    long_description = lines


def read(*parts):
    with codecs.open(os.path.join(cur_dir, *parts), 'r') as fp:
        return fp.read()


# Reference: https://github.com/pypa/pip/blob/master/setup.py
def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file,
        re.M,
    )
    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string.")


setup(
    name='codehere',
    version=find_version("codehere", "__init__.py"),
    description='Jupiter notebooks and py files compiler for seminars and students homework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tviskaron/codehere',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.so']},
    install_requires=[

    ],
    classifiers=[
        'Intended Audience :: Teachers, Students',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={"console_scripts": ["codehere=codehere.code_here:main"]},
)
