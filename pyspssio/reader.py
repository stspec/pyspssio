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


from ctypes import (Structure, 
                    byref, POINTER, create_string_buffer,
                    c_int, c_long, c_double, 
                    c_char, c_char_p)

from constants import (retcodes,
                       spss_datetime_formats_to_convert,
                       SPSS_ORIGIN_OFFSET,
                       S_TO_NS)

from header import Header




class Reader(Header):
    
    def __init__(self, *args, row_offset=0, row_limit=None, usecols=None,
                 chunksize=None, convert_datetimes=True,
                 include_user_missing=True, string_nan='', **kwargs):
        super().__init__(*args, **kwargs) 
              
        # adjust usecols
        if usecols is None:
            usecols = self.varNames
        elif isinstance(usecols, str):
            usecols = [x.strip() for x in usecols.split(',')]
            usecols = [var for var in usecols if var in self.varNames]
        elif callable(usecols):
            usecols = [var for var in self.varNames if usecols(var)]
        else:        
            usecols = [var for var in usecols if var in self.varNames]
           
        self.usecols = usecols
        self.convert_datetimes = convert_datetimes
        self.include_user_missing = include_user_missing

        self.caseRec = create_string_buffer(self.caseSize)
              
        self.dtype_double, \
        self.numeric_names, \
        self.numeric_slices, \
        self.datetime_names, \
        self.datetime_slices, \
        self.string_names, \
        self.string_slices = self._build_struct()
       
        self.chunksize = chunksize
        self.chunk = 0

        self.string_nan = string_nan

        # adjust row_limit
        if row_limit is None:
            row_limit = self.caseCount
        row_limit = min(row_limit, self.caseCount - row_offset)
        
        self.total_rows = row_limit
       
        if row_offset:
            self._seekNextCase(row_offset)
                      
    def __iter__(self):            
        return self
   
    def __next__(self):
        if self.chunk < self.total_rows:
            row_limit = min(self.chunksize, self.total_rows - self.chunk)
            df = self.readData(row_limit, self.convert_datetimes, self.include_user_missing)
            self.chunk += self.chunksize
            return df
        else:
            self.closeSPSS()
            del self.spssio
            raise StopIteration()

    def _seekNextCase(self, caseNumber):
        self.spssio.spssSeekNextCase(self.fh, c_long(caseNumber))
       
    def _wholeCaseIn(self, caseRec):
        """caseRec is a string buffer of caseSize

        see caseSize in Header class
        """

        func = self.spssio.spssWholeCaseIn        
        retcode = func(self.fh, caseRec)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))            
        return caseRec   

    @property
    def metadata(self):
        
        usecols = self.usecols
                
        # trim mrsets        
        multRespDefs = {}
        if len(self.multRespDefs):
            for setName, setAttr in self.multRespDefs.items():
                setAttr['variable_list'] = [x for x in setAttr['variable_list'] if x in usecols]
                if setAttr['variable_list']:
                    multRespDefs[setName] = setAttr
                
        return {
            'caseCount': self.caseCount,
            'fileAttributes': self.fileAttributes,
            'varNames': usecols,
            'varTypes': {k:v for k, v in self.varTypes.items() if k in usecols},
            'varFormats': {k:v for k, v in self.varFormats.items() if k in usecols},
            'varFormatsTuple': {k:v for k, v in self.varFormatsTuple.items() if k in usecols},
            'varLabels': {k:v for k, v in self.varLabels.items() if k in usecols},
            'varAlignments': {k:v for k, v in self.varAlignments.items() if k in usecols},
            'varColumnWidths': {k:v for k, v in self.varColumnWidths.items() if k in usecols},
            'varMeasureLevels': {k:v for k, v in self.varMeasureLevels.items() if k in usecols},
            'varRoles': {k:v for k, v in self.varRoles.items() if k in usecols},
            'varMissingValues': {k:v for k, v in self.varMissingValues.items() if k in usecols},
            'varValueLabels': {k:v for k, v in self.varValueLabels.items() if k in usecols},
            'multRespDefs': multRespDefs,
            'caseWeightVar': self.caseWeightVar
            }
    

    def _build_struct(self):
        usecols = self.usecols
        
        # get variable info
        varNames = self.varNames
        varTypes = self.varTypes
        varFormats = self.varFormatsTuple            
            
        # get buffer structure
        numeric_names = []
        numeric_formats = []
        numeric_offsets = []
        numeric_nbytes = []
        numeric_slices = [slice(0,0)]
        
        datetime_names = []
        datetime_formats = []
        datetime_offsets = []
        datetime_nbytes = []
        datetime_slices = [slice(0,0)]
        
        string_names = []
        string_slices = []

        offset = 0
        for varName in varNames:    
            varType = varTypes[varName]
            varFormat = varFormats[varName]
            if varType:
                nbytes = int(8 * -(varType // -8))
                sformat = 'a' + str(nbytes)
                if varName in usecols:
                    string_names.append(varName)
                    s = slice(offset, offset + nbytes)
                    string_slices.append(s)
            else:
                nbytes = 8
                sformat = 'd'
                if varName in usecols:
                    if varFormat[0] in spss_datetime_formats_to_convert:
                        datetime_names.append(varName)
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
                        numeric_names.append(varName)
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
        
        dtype_double = np.dtype('d')
        
        # endianness adjustments
        endianness = {0:'<', 1: '>'}.get(self.releaseInfo.get("big/little-endian code"))
                      
        if endianness:
            dtype_double = dtype_double.newbyteorder(endianness)
            
        return dtype_double, numeric_names, numeric_slices, datetime_names, datetime_slices, string_names, string_slices
            
    def read_data(self, row_limit=None, convert_datetimes=True, include_user_missing=True):
                                         
        def load_strings(case):
            return tuple(str(case[self.string_slices[idx]], self.encoding).rstrip()
                         for idx, varName in enumerate(self.string_names))
        
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
            return ((arr - SPSS_ORIGIN_OFFSET) * S_TO_NS).astype('datetime64[ns]', copy=False)             

        # create empty arrays
        n_arr = np.empty(shape=(row_limit, len(self.numeric_names)), dtype=self.dtype_double)
        d_arr = np.empty(shape=(row_limit, len(self.datetime_names)), dtype=self.dtype_double)
        s_arr = np.empty(shape=(row_limit, len(self.string_names)), dtype='O') 

        # load cases into arrays
        for row in range(row_limit):
            case = memoryview(self._wholeCaseIn(self.caseRec))  
            #return (load_numerics(case), struct_names)
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
            all_cols[col] = s_arr[: ,idx]

        for idx, col in enumerate(self.numeric_names):
            all_cols[col] = n_arr[:, idx]

        df = pd.DataFrame(all_cols, copy=False)

        # drop user missing values if specified
        if not include_user_missing:            
            varTypes = self.varTypes
            for col, missing in self.varMissingValues.items():
                if col in df.columns:
                    df.loc[df[col].isin(missing.get('values', [])), col] = '' if varTypes[col] else np.nan
                    high = missing.get('hi')
                    low = missing.get('lo')
                    if high is not None and low is not None:
                        df.loc[df[col].between(low, high, inclusive='both'), col] = np.nan
        
        # use user-defined string nan value
        if self.string_nan != '':
            df = df.replace('', self.string_nan, regex=False)

        return df
    

                 