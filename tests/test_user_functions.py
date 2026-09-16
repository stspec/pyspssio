from pathlib import Path

import pytest

import pyspssio

test_file = Path(__file__).parent / "files" / "test_file.sav"


def test_read_sav():
    pyspssio.read_sav(test_file, row_limit=10)


def test_write_sav(tmp_path):
    write_path = tmp_path / "test_write.sav"
    df, meta = pyspssio.read_sav(test_file, row_limit=10)
    pyspssio.write_sav(write_path, df, meta)


def test_append_sav(tmp_path):
    append_path = tmp_path / "test_write.sav"
    df, meta = pyspssio.read_sav(test_file, row_limit=10)
    pyspssio.write_sav(append_path, df, meta)
    pyspssio.append_sav(append_path, df)
    df_written, _ = pyspssio.read_sav(append_path)
    assert len(df_written) == (len(df) * 2)
