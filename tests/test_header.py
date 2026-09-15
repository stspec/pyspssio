from pathlib import Path

import pytest

import pyspssio

from . import data


@pytest.fixture(scope="module")
def spss_header():
    spss_path = Path(__file__).parent / "files" / "test_header.sav"
    with pyspssio.Header(spss_path, mode="w") as writer:
        yield writer


def test_open(spss_header):
    assert spss_header.mode == "wb"


def test_file_attributes(spss_header):
    spss_header.file_attributes = data.file_attributes
    assert spss_header.file_attributes == {
        str(k): str(v) for k, v in data.file_attributes.items()
    }


def test_var_types(spss_header):
    spss_header.var_types = data.var_types
    assert spss_header.var_types == data.var_types


def test_var_formats(spss_header):
    spss_header.var_formats = data.var_formats
    assert spss_header.var_formats_tuple == {
        k: pyspssio.header.varformat_to_tuple(v) for k, v in data.var_formats.items()
    }


def test_var_measure_levels(spss_header):
    spss_header.var_measure_levels = data.var_measure_levels
    assert spss_header.var_measure_levels == {
        k: pyspssio.constants_map.measure_levels_str.get(v, v)
        for k, v in data.var_measure_levels.items()
    }


def test_var_alignments(spss_header):
    spss_header.var_alignments = data.var_alignments
    assert spss_header.var_alignments == {
        k: pyspssio.constants_map.alignments_str.get(v, v)
        for k, v in data.var_alignments.items()
    }


def test_var_widths(spss_header):
    spss_header.var_widths = data.var_widths
    assert spss_header.var_widths == data.var_widths


def test_var_labels(spss_header):
    spss_header.var_labels = data.var_labels
    assert spss_header.var_labels == data.var_labels


def test_var_roles(spss_header):
    spss_header.var_roles = data.var_roles
    assert spss_header.var_roles == {
        k: pyspssio.constants_map.roles_str.get(v, v) for k, v in data.var_roles.items()
    }


def test_var_value_labels(spss_header):
    spss_header.var_value_labels = data.var_value_labels
    assert spss_header.var_value_labels == data.var_value_labels


def test_mrsets(spss_header):
    spss_header.mrsets = data.mrsets
    # assert all mrsets were successfully written
    # response has several extra fields
    assert spss_header.mrsets.keys() == data.mrsets.keys()


def test_case_weight_var(spss_header):
    spss_header.case_weight_var = "numeric_var"
    assert spss_header.case_weight_var == "numeric_var"


def test_var_missing_values(spss_header):
    spss_header.var_missing_values = data.var_missing_values
    assert spss_header.var_missing_values == data.var_missing_values


def test_commit_header(spss_header):
    spss_header.commit_header()
