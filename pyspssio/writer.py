# -*- coding: utf-8 -*-
# =============================================================================
# COPYRIGHT NOTICE
# =============================================================================
#
# Copyright (c) 2022 Steven Spector
#
# The pyspssio python package is distributed under the MIT license,
# EXCLUDING files from the IBM I/O Modules for SPSS Statistics
# which are covered under a different license.
#
# License information pertaining to the IBM I/O Modules for SPSS Statistics
# is available in the LICENSE document.
# =============================================================================

from ctypes import *
from typing import Union
from types import SimpleNamespace

import os
import warnings
import psutil
import numpy as np
import pandas as pd
from pandas import DataFrame

from pandas.api.types import (
    is_numeric_dtype,
    is_string_dtype,
    is_object_dtype,
    is_datetime64_any_dtype,
    is_timedelta64_dtype,
)

from .errors import SPSSWarning, SPSSError, warn_or_raise
from . import config
from .constants import *
from .constants_map import *
from .header import Header, varformat_to_tuple


class Writer(Header):
    """Class for writing SPSS file"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _whole_case_out(self, case_record):
        """case_record is a string buffer"""

        func = self.spssio.spssWholeCaseOut
        func.argtypes = [c_int, c_char_p]
        retcode = func(self.fh, case_record)
        warn_or_raise(retcode, func)

    def _set_value_char(self, var_name, value):
        var_handle = self._get_var_handle(var_name.encode(self.encoding))
        func = self.spssio.spssSetValueChar
        func.argtypes = [c_int, c_double, c_char_p]
        retcode = func(self.fh, var_handle, value)
        warn_or_raise(retcode, func, var_name, value)

    def _set_value_numeric(self, var_name, value):
        var_handle = self._get_var_handle(var_name.encode(self.encoding))
        func = self.spssio.spssSetValueNumeric
        func.argtypes = [c_int, c_double, c_double]
        retcode = func(self.fh, var_handle, value)
        warn_or_raise(retcode, func, var_name, value)

    def commit_case_record(self):
        """Commit case record

        Call function after setting values with set_value
        Do not use with whole_case_out"""

        func = self.spssio.spssCommitCaseRecord
        retcode = func(self.fh)
        warn_or_raise(retcode, func)

    def write_header(self, df: DataFrame, metadata: Union[dict, SimpleNamespace] = None, **kwargs):
        """Write metadata properties

        Parameters
        ----------
        df
            DataFrame
        metadata
            Dictionary of Header attributes to use (see Header class for more detail)
        **kwargs
            Additional arguments, including individual metadata attributes.
            Note that metadata attributes supplied here take precedence.
        """

        compression = {".sav": 1, ".zsav": 2}.get(os.path.splitext(self.filename)[1].lower())
        self.compression = compression

        if metadata is None:
            metadata = {}
        elif isinstance(metadata, SimpleNamespace):
            metadata = metadata.__dict__

        # combine, with preference to kwargs
        metadata = {**metadata, **kwargs}

        metadata["var_types"] = metadata.get("var_types", {})
        metadata["var_formats"] = metadata.get("var_formats", {})
        metadata["var_measure_levels"] = metadata.get("var_measure_levels", {})

        # convert all var_formats to tuple structure
        # ignore var_formats_tuple if supplied
        # var_formats can be either plain or tuple structure
        metadata["var_formats"] = {
            var_name: varformat_to_tuple(var_format)
            for var_name, var_format in metadata["var_formats"].items()
        }

        dtypes = df.dtypes.to_dict()
        var_types = {}

        encoding = self.encoding

        # setup types, formats, levels
        for col, dtype in dtypes.items():
            if (
                metadata["var_types"].get(col)
                or is_string_dtype(dtypes.get(col))
                or is_object_dtype(dtypes.get(col))
            ):
                var_type = (
                    df[col]
                    .fillna("")
                    .apply(lambda x: (x if hasattr(x, "decode") else len(str(x).encode(encoding))))
                    .max()
                )
                var_type = max(var_type, metadata["var_types"].get(col, 1))
                var_type = min(var_type, SPSS_MAX_LONGSTRING)
                var_types[col] = var_type
                var_format = metadata["var_formats"].get(col, (1, 1, 0))
                metadata["var_formats"][col] = (
                    var_format[0] if var_format[0] in spss_string_formats else 1,
                    var_type,
                    0,
                )
            elif is_timedelta64_dtype(dtype):
                var_types[col] = 0
                metadata["var_formats"][col] = metadata["var_formats"].get(
                    col, config.default_time_format
                )
                metadata["var_measure_levels"][col] = metadata["var_measure_levels"].get(col, 3)
            elif is_datetime64_any_dtype(dtype):
                var_types[col] = 0
                metadata["var_formats"][col] = metadata["var_formats"].get(
                    col, config.default_datetime_format
                )
                metadata["var_measure_levels"][col] = metadata["var_measure_levels"].get(col, 3)
            else:
                var_types[col] = 0
                metadata["var_formats"][col] = metadata["var_formats"].get(
                    col, config.default_numeric_format
                )
                metadata["var_measure_levels"][col] = metadata["var_measure_levels"].get(col, 3)

        # initiate variables
        for col in df.columns:
            self._add_var(col, var_types[col])

        # set optional header attributes
        attr_to_ignore = [
            "case_count",
            "encoding",
            "var_names",
            "var_types",
            "var_formats_tuple",
            "var_compat_names",
        ]
        attrs = [attr for attr in dir(self) if attr[0] != "_" and attr not in attr_to_ignore]

        # catch Exceptions for non-critical attributes
        failed_to_set = {}
        for attr, v in metadata.items():
            if attr in attrs and v:
                try:
                    setattr(self, attr, v)
                except SPSSError as e:
                    failed_to_set[attr] = e

        if failed_to_set:
            warnings.warn(
                SPSSWarning(
                    "Errors occurred while writing header attributes:\n\n"
                    + "\n\n".join((f"{attr}: {error}" for attr, error in failed_to_set.items()))
                    + "\n"
                ),
                stacklevel=2,
            )

        # commit header
        self.commit_header()

    def write_data_by_val(self, df: DataFrame):
        """Write data by variable/value

        Parameters
        ----------
        df
            DataFrame

        Notes
        -----
        Slower than whole_case_out
        Use when appending to an existing data set and variable order doesn't align
        """

        pd_origin = pd.to_datetime(0)

        var_types = self.var_types
        var_handles = self.var_handles

        dtypes = df.dtypes.to_dict()

        idx_cols = dict(enumerate(df.columns))

        write_c = self.spssio.spssSetValueChar
        write_c.argtypes = [c_int, c_double, c_char_p]
        write_n = self.spssio.spssSetValueNumeric
        write_n.argtypes = [c_int, c_double, c_double]

        for row in df.itertuples(index=False, name=None):
            for idx, col in idx_cols.items():
                value = row[idx]
                if pd.notna(value):

                    # string
                    if var_types[col]:
                        value = value.encode(self.encoding)
                        retcode = write_c(self.fh, var_handles[col], value)
                        warn_or_raise(retcode, write_c, col, value)

                    # time
                    elif is_timedelta64_dtype(dtypes[col]):
                        value = value.total_seconds()
                        retcode = write_n(self.fh, var_handles[col], value)
                        warn_or_raise(retcode, write_n, col, value)

                    # datetime
                    elif is_datetime64_any_dtype(dtypes[col]):
                        value = (value - pd_origin).total_seconds() + SPSS_ORIGIN_OFFSET
                        retcode = write_n(self.fh, var_handles[col], value)
                        warn_or_raise(retcode, write_n, col, value)

                    # numeric
                    else:
                        retcode = write_n(self.fh, var_handles[col], value)
                        warn_or_raise(retcode, write_n, col, value)

            self.commit_case_record()

    def write_data(self, df: DataFrame, **kwargs):
        """Write data to file

        Parameters
        ----------
        df
            DataFrame
        """

        # basic info
        var_types = self.var_types
        sysmis = self.sysmis
        encoding = self.encoding

        pd_origin = pd.to_datetime(0)

        def get_buffer_size(var_type):
            return -8 * (var_type // -8)

        string_padder = " ".encode(encoding)
        string_cols = {
            var_name: get_buffer_size(var_type)
            for var_name, var_type in var_types.items()
            if var_type
        }

        endianness = {0: "<", 1: ">"}.get(self.release_info.get("big/little-endian code"), "")

        write_types = {}
        for col, var_type in var_types.items():
            if var_type:
                write_types[col] = endianness + "V" + str(string_cols[col])
            else:
                write_types[col] = endianness + "d"

        dtypes = df.dtypes.to_dict()

        def finalize(col):
            buffer_size = string_cols.get(col.name)
            if buffer_size:
                return col.apply(
                    lambda x: (
                        x if hasattr(x, "decode") else (b"" if pd.isna(x) else x.encode(encoding))
                    ).ljust(buffer_size, string_padder)
                )
            elif is_timedelta64_dtype(dtypes[col.name]):
                return col.dt.total_seconds().to_numpy(dtype=np.float64, na_value=sysmis)
            elif is_datetime64_any_dtype(dtypes[col.name]):
                return ((col - pd_origin).dt.total_seconds() + SPSS_ORIGIN_OFFSET).to_numpy(
                    dtype=np.float64, na_value=sysmis
                )
            else:
                return col.to_numpy(dtype=np.float64, na_value=sysmis)

        # choose chunksize
        total_records = len(df.index)
        case_size = self.case_size
        mem_to_use = int(psutil.virtual_memory().available * kwargs.get("memory_allocation", 0.1))
        chunksize = max(1, mem_to_use // case_size)

        # write data
        for i in range(0, total_records, chunksize):
            chunk = (
                df.iloc[i : i + chunksize]
                .transform(finalize)
                .to_records(index=False, column_dtypes=write_types)
            )
            for record in chunk:
                case_record = record.tobytes()
                self._whole_case_out(case_record)
