from pathlib import Path

import pytest

import pyspssio


@pytest.fixture(scope="module")
def spss_reader():
    spss_path = Path(__file__).parent / "files" / "test_file.sav"
    with pyspssio.Reader(spss_path) as reader:
        yield reader


def test_open(spss_reader):
    assert spss_reader.mode == "rb"


def test_metadata(spss_reader):
    assert isinstance(spss_reader.metadata, dict)


def test_read_data(spss_reader):
    spss_reader.read_data(row_limit=10)
