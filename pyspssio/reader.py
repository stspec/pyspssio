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


import pandas as pd
import numpy as np

from ctypes import *

from .errors import warn_or_raise
from . import config
from .constants import *
from .header import Header


class Reader(Header):
    """Class for reading metadata and data"""

    def __init__(
        self,
        *args,
        row_offset=0,
        row_limit=None,
        usecols=None,
        chunksize=None,
        convert_datetimes=True,
        include_user_missing=True,
        string_nan="",
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        # adjust usecols
        if usecols is None:
            usecols = self.var_names
        elif isinstance(usecols, str):
            usecols = [x.strip() for x in usecols.split(",")]
            usecols = [col for col in usecols if col in self.var_names]
        elif callable(usecols):
            usecols = [col for col in self.var_names if usecols(col)]
        else:
            usecols = [col for col in usecols if col in self.var_names]

        self.usecols = usecols
        self.convert_datetimes = convert_datetimes
        self.include_user_missing = include_user_missing

        self.case_record = create_string_buffer(self.case_size)

        (
            self.dtype_double,
            self.numeric_names,
            self.numeric_slices,
            self.datetime_names,
            self.datetime_slices,
            self.string_names,
            self.string_slices,
        ) = self._build_struct()

        self.chunksize = chunksize
        self.chunk = 0

        self.string_nan = string_nan

        # adjust row_limit
        if row_limit is None:
            row_limit = self.case_count
        row_limit = min(row_limit, self.case_count - row_offset)

        self.total_rows = row_limit

        if row_offset:
            self._seek_next_case(row_offset)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            if self.chunk < self.total_rows:
                row_limit = min(self.chunksize, self.total_rows - self.chunk)
                df = self.read_data(
                    row_limit=row_limit,
                    convert_datetimes=self.convert_datetimes,
                    include_user_missing=self.include_user_missing,
                )
                df.index = pd.RangeIndex(self.chunk, self.chunk + row_limit)
                self.chunk += self.chunksize
                return df
            else:
                raise StopIteration()
        except Exception:
            self._exit_cleanup()
            raise

    def _seek_next_case(self, case_number):
        func = self.spssio.spssSeekNextCase
        retcode = func(self.fh, c_long(case_number))
        warn_or_raise(retcode, func, case_number)

    def _whole_case_in(self, case_record):
        """caseRec is a string buffer of caseSize

        see caseSize in Header class
        """

        func = self.spssio.spssWholeCaseIn
        retcode = func(self.fh, case_record)
        warn_or_raise(retcode, func)
        return case_record

    @property
    def metadata(self):
        """Metadata property"""

        usecols = self.usecols

        variable_properties = [
            "var_types",
            "var_formats",
            "var_formats_tuple",
            "var_labels",
            "var_alignments",
            "var_column_widths",
            "var_measure_levels",
            "var_roles",
            "var_missing_values",
            "var_value_labels",
        ]

        # trim mrsets
        mrsets = {}
        if len(self.mrsets):
            for set_name, set_attr in self.mrsets.items():
                set_attr["variable_list"] = [
                    col for col in set_attr["variable_list"] if col in usecols
                ]
                if set_attr["variable_list"]:
                    mrsets[set_name] = set_attr

        metadata = {
            "file_attributes": self.file_attributes,
            "encoding": self.encoding,
            "case_count": self.case_count,
            "case_weight_var": self.case_weight_var,
            "mrsets": mrsets,
        }

        for prop in variable_properties:
            metadata[prop] = {k: v for k, v in getattr(self, prop).items() if k in usecols}

        return metadata

    def _build_struct(self):
        usecols = self.usecols

        # get variable info
        var_names = self.var_names
        var_types = self.var_types
        var_formats = self.var_formats_tuple

        # get buffer structure
        numeric_names = []
        numeric_formats = []
        numeric_offsets = []
        numeric_nbytes = []
        numeric_slices = [slice(0, 0)]

        datetime_names = []
        datetime_formats = []
        datetime_offsets = []
        datetime_nbytes = []
        datetime_slices = [slice(0, 0)]

        string_names = []
        string_slices = []

        offset = 0
        for var_name in var_names:
            var_type = var_types[var_name]
            var_format = var_formats[var_name]
            if var_type:
                nbytes = int(8 * -(var_type // -8))
                sformat = "a" + str(nbytes)
                if var_name in usecols:
                    string_names.append(var_name)
                    s = slice(offset, offset + nbytes)
                    string_slices.append(s)
            else:
                nbytes = 8
                sformat = "d"
                if var_name in usecols:
                    if var_format[0] in config.spss_datetime_formats_to_convert:
                        datetime_names.append(var_name)
                        datetime_formats.append(sformat)
                        datetime_offsets.append(offset)
                        datetime_nbytes.append(nbytes)
                        s = slice(offset, offset + nbytes)
                        s_prev = datetime_slices[-1]
                        if s.start == s_prev.stop:
                            datetime_slices[-1] = slice(s_prev.start, s.stop)
                        else:
                            datetime_slices.append(s)
                    else:
                        numeric_names.append(var_name)
                        numeric_formats.append(sformat)
                        numeric_offsets.append(offset)
                        numeric_nbytes.append(nbytes)
                        s = slice(offset, offset + nbytes)
                        s_prev = numeric_slices[-1]
                        if s.start == s_prev.stop:
                            numeric_slices[-1] = slice(s_prev.start, s.stop)
                        else:
                            numeric_slices.append(s)
            offset += nbytes

        dtype_double = np.dtype("d")

        # endianness adjustments
        endianness = {0: "<", 1: ">"}.get(self.release_info.get("big/little-endian code"))

        if endianness:
            dtype_double = dtype_double.newbyteorder(endianness)

        return (
            dtype_double,
            numeric_names,
            numeric_slices,
            datetime_names,
            datetime_slices,
            string_names,
            string_slices,
        )

    def read_data(self, row_limit=None, convert_datetimes=None, include_user_missing=None):
        """Read data"""

        if row_limit:
            row_limit = min(row_limit, self.total_rows)
        else:
            row_limit = self.total_rows

        if convert_datetimes is None:
            convert_datetimes = self.convert_datetimes

        if include_user_missing is None:
            include_user_missing = self.include_user_missing

        def load_strings(case):
            return tuple(
                str(case[self.string_slices[idx]], self.encoding).rstrip()
                for idx, var_name in enumerate(self.string_names)
            )

        def load_numerics(case):
            b = bytearray()
            for s in self.numeric_slices:
                b += case[s]
            return np.frombuffer(b, dtype=self.dtype_double)

        def load_datetimes(case):
            b = bytearray()
            for s in self.datetime_slices:
                b += case[s]
            return np.frombuffer(b, dtype=self.dtype_double)

        def replace_sysmis(arr):
            return np.where(arr == self.sysmis, np.nan, arr)

        def convert_dt(arr):
            return ((arr - SPSS_ORIGIN_OFFSET) * S_TO_NS).astype("datetime64[ns]", copy=False)

        # create empty arrays
        n_arr = np.empty(shape=(row_limit, len(self.numeric_names)), dtype=self.dtype_double)
        d_arr = np.empty(shape=(row_limit, len(self.datetime_names)), dtype=self.dtype_double)
        s_arr = np.empty(shape=(row_limit, len(self.string_names)), dtype="O")

        # load cases into arrays
        for row in range(row_limit):
            case = memoryview(self._whole_case_in(self.case_record))
            # return (load_numerics(case), struct_names)
            n_arr[row] = load_numerics(case)
            d_arr[row] = load_datetimes(case)
            s_arr[row] = load_strings(case)

        # replace system missing
        n_arr = replace_sysmis(n_arr)
        d_arr = replace_sysmis(d_arr)

        # convert datetimes
        if convert_datetimes and len(d_arr):
            d_arr = convert_dt(d_arr)

        # create final dataframe
        all_cols = {col: None for col in self.usecols}

        for idx, col in enumerate(self.datetime_names):
            all_cols[col] = d_arr[:, idx]

        for idx, col in enumerate(self.string_names):
            all_cols[col] = s_arr[:, idx]

        for idx, col in enumerate(self.numeric_names):
            all_cols[col] = n_arr[:, idx]

        df = pd.DataFrame(all_cols, copy=False)

        # drop user missing values if specified
        if not include_user_missing:
            var_types = self.var_types
            for col, missing in self.var_missing_values.items():
                if col in df.columns:
                    df.loc[df[col].isin(missing.get("values", [])), col] = (
                        "" if var_types[col] else np.nan
                    )
                    high = missing.get("hi")
                    low = missing.get("lo")
                    if high is not None and low is not None:
                        df.loc[df[col].between(low, high, inclusive="both"), col] = np.nan

        # use user-defined string nan value
        if self.string_nan != "":
            df = df.replace("", self.string_nan, regex=False)

        return df
