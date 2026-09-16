from pathlib import Path

import pytest

import pyspssio


@pytest.fixture(scope="module")
def spss_data():
    spss_path = Path(__file__).parent / "files" / "test_file.sav"
    df, meta = pyspssio.read_sav(spss_path, row_limit=10)
    return df, meta


@pytest.fixture(scope="module")
def spss_writer(tmp_path_factory, spss_data):
    spss_path = tmp_path_factory.mktemp("tmp") / "test_write.sav"
    with pyspssio.Writer(spss_path) as writer:
        yield writer


def test_open(spss_writer):
    assert spss_writer.mode == "wb"


def test_write_header(spss_writer, spss_data):
    df, meta = spss_data
    spss_writer.write_header(df, meta)


def test_write_data(spss_writer, spss_data):
    df, _ = spss_data
    spss_writer.write_data(df)
