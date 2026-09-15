from pathlib import Path

import pytest

import pyspssio

from . import data


@pytest.fixture(scope="module")
def spss_writer():
    spss_path = Path(__file__).parent / "files" / "test_write.sav"
    with pyspssio.Writer(spss_path) as writer:
        yield writer


def test_open(spss_writer):
    assert spss_writer.mode == "wb"


def test_write_header(spss_writer):
    spss_writer.write_header(data.df, data.metadata)


def test_write_data(spss_writer):
    spss_writer.write_data(data.df)
