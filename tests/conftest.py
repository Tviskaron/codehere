from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def sample_py(fixtures_dir):
    return str(fixtures_dir / "sample.py")


@pytest.fixture
def sample_ipynb(fixtures_dir):
    return str(fixtures_dir / "sample.ipynb")


@pytest.fixture
def sample_md(fixtures_dir):
    return str(fixtures_dir / "sample.md")
