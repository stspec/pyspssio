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



from reader import Reader
from writer import Writer




def read_metadata(spss_file, usecols=None, set_locale=None):
    """Reads metadata attributes from SPSS file

    Parameters
    ----------
    spss_file : str
        Filepath of SPSS file (.sav or .zsav)
    usecols : str or tuple or list or callable, default=None
        Specifies which columns to keep for column-related metadata; 
        Use None for all columns
    set_locale : str, default=None
        Sets I/O locale when operating in codepage mode
        Default None to use system locale

    Returns
    -------
    dict
        A dictionary of metadata attributes; 
        See Header class for more detail
    """

    with Reader(spss_file, mode='r', usecols=usecols, set_locale=set_locale) as sav:
        return sav.metadata




def read_sav(spss_file, row_offset=0, row_limit=None, usecols=None,
             convert_datetimes=True, include_user_missing=True,
             chunksize=None, set_locale=None, string_nan=''):
    """Read data and metadata from SPSS file
    
    Parameters
    ----------
    spss_file : str
        Filepath of SPSS file (.sav or .zsav)
    row_offset : int, default=0
        Specifies which record number to start reading from
    row_limit : int, default=None
        Maximum number of records to return.
    usecols : str or tuple or list or callable, default=None
        Specifies which columns to keep; 
        Use None for all columns
    convert_datetimes : bool, default=True  
        Convert SPSS datetimes to Python/Pandas datetime columns; 
        False returns float, seconds from October 15, 1582
    include_user_missing : bool, default=True
        Whether to keep user missing values or 
        replace them with NaN (numeric) and '' (strings)
    chunksize : int, default=None
        Number of rows to return per chunk
    set_locale : str, default=None  
        Sets I/O locale when operating in codepage mode; 
        Default None to use system locale
    string_nan : default=''
        Value to return for empty strings

    Returns
    -------
    tuple : default
        - dataframe
        - dict (metadata)
    generator : if chunksize is defined
        - dataframe(s) of chunksize (no metadata dict)
    """

    if chunksize:
        return Reader(spss_file, mode='r',
                      row_offset=row_offset, row_limit=row_limit,
                      usecols=usecols, chunksize=chunksize,
                      convert_datetimes=convert_datetimes, 
                      include_user_missing=include_user_missing,
                      set_locale=set_locale, string_nan=string_nan)
    else:    
        with Reader(spss_file, mode='r', 
                    row_offset=row_offset, row_limit=row_limit,
                    usecols=usecols, chunksize=chunksize,
                    convert_datetimes=convert_datetimes,
                    include_user_missing=include_user_missing,
                    set_locale=set_locale, string_nan=string_nan) as sav:
            metadata = sav.metadata
            df = sav.read_data(sav.total_rows, convert_datetimes, include_user_missing)
        return df, metadata




def write_sav(spss_file, df,
              unicode=True, set_locale=None,
              metadata=None, **kwargs):
    """Write dataframe to SPSS (.sav or .zsav) file

    Parameters
    ----------
    spss_file : str
        Filepath of SPSS file (.sav or .zsav) to create
    df : dataframe
        Pandas dataframe 
    unicode : bool, default=True
        Whether to write the file in unicode or codepage mode
    set_locale : str, default=None
        Sets I/O locale when operating in codepage mode
        Default None to use system locale
    metadata : dict, default=None
        Dictionary of Header attributes to apply (e.g., varLabels, varValueLabels, etc.);
        See Header class for more detail
    **kwargs
        Option to provide other arguments, 
        including individual metadata attributes; 
        note that metadata attributes supplied here take precedence
    """

    with Writer(spss_file, mode='w', unicode=unicode, set_locale=set_locale) as sav:
        sav.writeHeader(df, metadata, **kwargs)
        sav.writeData(df, **kwargs)




def append_sav(spss_file, df, set_locale=None, **kwargs):
    """Append existing SPSS (.sav or .zsav) file with additional records
    
    Parameters
    ----------
    spss_file : str
        Filepath of SPSS file (.sav or .zsav) to append
    df : dataframe
        Pandas dataframe 
    set_locale : str, default=None
        Sets I/O locale when operating in codepage mode
        Default None to use system locale
    **kwargs
        
    Cannot modify metadata when appending new records. 
    Be careful with strings that might be longer than the allowed width.

    set_locale is probably not necessary since file encoding 
    is obtained from the SPSS header information.
    """

    with Writer(spss_file, mode='a', set_locale=set_locale) as sav:
        if df.columns.tolist() == sav.varNames:
            sav.writeData(df, **kwargs)
        else:
            sav.writeDataByVal(df, **kwargs)

                