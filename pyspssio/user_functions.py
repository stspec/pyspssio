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

from typing import Union, Any, Tuple, Generator
from pandas import DataFrame
from .reader import Reader
from .writer import Writer


def read_metadata(
    spss_file: str,
    usecols: Union[list, tuple, str, callable, None] = None,
    locale: str = None,
) -> dict:
    """Reads metadata attributes from SPSS file

    Parameters
    ----------
    spss_file
        SPSS filename (.sav or .zsav)
    usecols
        Columns to use (None for all columns)
    locale
        Locale to use when I/O module is operating in codepage mode

    Returns
    -------
    dict
        Header properties (see Header class for more detail)

    Examples
    --------
    >>> meta = pyspssio.read_metadata("spss_file.sav")

    """

    with Reader(spss_file, mode="r", usecols=usecols, locale=locale) as sav:
        return sav.metadata


def read_sav(
    spss_file: str,
    row_offset: int = 0,
    row_limit: int = None,
    usecols: Union[list, tuple, str, callable, None] = None,
    convert_datetimes: bool = True,
    include_user_missing: bool = True,
    chunksize: int = None,
    locale: str = None,
    string_nan: Any = "",
) -> Union[Tuple[DataFrame, dict], Generator[DataFrame, None, None]]:
    """Read data and metadata from SPSS file

    Parameters
    ----------
    spss_file
        SPSS filename (.sav or .zsav)
    row_offset
        Number of rows to skip
    row_limit
        Maximum number of rows to return
    usecols
        Columns to use (None for all columns)
    convert_datetimes
        Convert SPSS datetimes to Python/Pandas datetime columns;
        False returns seconds from October 15, 1582 (SPSS start date)
    include_user_missing
        Whether to keep user missing values or
        replace them with NaN (numeric) and "" (strings)
    chunksize
        Number of rows to return per chunk
    locale
        Locale to use when I/O module is operating in codepage mode
    string_nan
        Value to return for empty strings

    Returns
    -------
    tuple
        DataFrame, metadata
    generator
        DataFrame(s) with chunksize number of rows (only if chunksize is specified)

    Examples
    --------

    Read data and metadata::

        df, meta = pyspssio.read_sav("spss_file.sav")


    Read metadata only::

        meta = pyspssio.read_metadata("spss_file.sav")


    Read data in chunks of chunksize (number of rows/records)::

        for df in pyspssio.read_sav("spss_file.sav", chunksize=1000):
            # do something

    """

    if chunksize:
        return Reader(
            spss_file,
            mode="r",
            row_offset=row_offset,
            row_limit=row_limit,
            usecols=usecols,
            chunksize=chunksize,
            convert_datetimes=convert_datetimes,
            include_user_missing=include_user_missing,
            locale=locale,
            string_nan=string_nan,
        )
    else:
        with Reader(
            spss_file,
            mode="r",
            row_offset=row_offset,
            row_limit=row_limit,
            usecols=usecols,
            chunksize=chunksize,
            convert_datetimes=convert_datetimes,
            include_user_missing=include_user_missing,
            locale=locale,
            string_nan=string_nan,
        ) as sav:

            metadata = sav.metadata
            df = sav.read_data(sav.total_rows, convert_datetimes, include_user_missing)

        return df, metadata


def write_sav(
    spss_file: str,
    df: DataFrame,
    metadata: dict = None,
    unicode: bool = True,
    locale: str = None,
    **kwargs
) -> None:
    """Write SPSS file (.sav or .zsav) from DataFrame

    Parameters
    ----------
    spss_file
        SPSS filename (.sav or .zsav)
    df
        DataFrame
    metadata
        Dictionary of Header attributes to use (see Header class for more detail)
    unicode
        Whether to write the file in unicode (True) or codepage (False) mode
    locale
        Locale to use when I/O module is operating in codepage mode
    **kwargs
        Additional arguments, including individual metadata attributes.
        Note that metadata attributes supplied here take precedence.

    Examples
    --------
    >>> pyspssio.write_sav("spss_file.sav", df, metadata=meta)

    """

    with Writer(spss_file, mode="w", unicode=unicode, locale=locale) as sav:
        sav.write_header(df=df, metadata=metadata, **kwargs)
        sav.write_data(df=df, **kwargs)


def append_sav(spss_file: str, df: DataFrame, locale: str = None, **kwargs) -> None:
    """Append existing SPSS file (.sav or .zsav) with additional records

    Parameters
    ----------
    spss_file
        SPSS filename (.sav or .zsav)
    df
        DataFrame
    locale
        Locale to use when I/O module is operating in codepage mode
    **kwargs
        Additional arguments

    Notes
    -----
    Cannot modify metadata when appending new records.
    Be careful with strings that might be longer than the allowed width.

    It may or may not be necessary to manually set locale since file encoding
    information is obtained from the SPSS header information.

    Examples
    --------
    >>> pyspssio.append_sav("spss_file.sav", df)

    """

    with Writer(spss_file, mode="a", locale=locale) as sav:
        if df.columns.tolist() == sav.var_names:
            sav.write_data(df, **kwargs)
        else:
            sav.write_data_by_val(df, **kwargs)
