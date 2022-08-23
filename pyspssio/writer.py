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

import os
import pandas as pd
import numpy as np
import psutil

from pandas.api.types import is_numeric_dtype, is_string_dtype, is_object_dtype, is_datetime64_any_dtype

from ctypes import c_int, c_double, c_char_p

from constants import (retcodes,
                       spss_string_formats,
                       SPSS_ORIGIN_OFFSET,
                       SPSS_MAX_LONGSTRING)

import config
from header import Header, varFormat_to_varFormatTuple




class Writer(Header):
    
    def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       
       
    def _wholeCaseOut(self, caseRec):
        """caseRec is a string buffer        
        """
        
        func = self.spssio.spssWholeCaseOut
        func.argtypes = [c_int, c_char_p]        
        retcode = func(self.fh, caseRec)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
            
    def setValueChar(self, varName, value):
        varHandle = self._getVarHandle(varName.encode(self.encoding))
        func = self.spssio.spssSetValueChar
        func.argtypes = [c_int, c_double, c_char_p]
        retcode = func(self.fh, varHandle, value)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
            
    def setValueNumeric(self, varName, value):
        varHandle = self._getVarHandle(varName.encode(self.encoding))
        func = self.spssio.spssSetValueNumeric
        func.argtypes = [c_int, c_double, c_double]
        retcode = func(self.fh, varHandle, value)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))  
            
    def commitCaseRecord(self):
        retcode = self.spssio.spssCommitCaseRecord(self.fh)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
            
    def writeHeader(self, df, metadata=None, **kwargs):
        
        compression = {'.sav': 1, '.zsav': 2}.get(os.path.splitext(self.filename)[1].lower())        
        self.compression = compression
        
        if metadata is None:
            metadata = {}
        
        # combine, with preference to kwargs
        metadata = {**metadata, **kwargs}        
                  
        metadata['varTypes'] = metadata.get('varTypes', {})
        metadata['varFormats'] = metadata.get('varFormats', {})
        metadata['varMeasureLevels'] = metadata.get('varMeasureLevels', {})

        # convert all varFormats to tuple structure
        # ignores varFormatsTuple if supplied
        # varFormats can be either plain or tuple structure
        metadata['varFormats'] = {varName: varFormat_to_varFormatTuple(varFormat)
                                  for varName, varFormat in metadata['varFormats'].items()}

        dtypes = df.dtypes.to_dict()
        varTypes = {}
               
        encoding = self.encoding
                          
        # setup varTypes, formats, levels
        for col, dtype in dtypes.items():           
            if metadata['varTypes'].get(col) or is_string_dtype(dtypes.get(col)) or is_object_dtype(dtypes.get(col)):
                varType = min(SPSS_MAX_LONGSTRING,
                              max(metadata['varTypes'].get(col, 1),
                                  df[col].fillna('').apply(lambda x: (x if hasattr(x, 'decode') else len(str(x).encode(encoding)))).max()))
                varTypes[col] = varType
                varFormat = metadata['varFormats'].get(col, (1,1,0))[0]
                metadata['varFormats'][col] = (varFormat if varFormat in spss_string_formats else 1, varType, 0)                 
            elif is_datetime64_any_dtype(dtype):
                varTypes[col] = 0
                metadata['varFormats'][col] = metadata['varFormats'].get(col, config.default_datetime_format)
                metadata['varMeasureLevels'][col] = metadata['varMeasureLevels'].get(col, 3)
            else:
                varTypes[col] = 0
                metadata['varFormats'][col] = metadata['varFormats'].get(col, config.default_numeric_format)
                metadata['varMeasureLevels'][col] = metadata['varMeasureLevels'].get(col, 3)
                                
        # initiate variables
        for col in df.columns:                         
            self._addVar(col, varTypes[col])         
               
        # set header attributes
        attr_to_ignore = ['caseCount', 'varNames', 'varTypes', 'varFormatsTuple']
        attrs = [attr for attr in dir(self) if attr[0] != '_' and attr not in attr_to_ignore]
        
        failed_to_set = {}
        for attr, v in metadata.items():
            if attr in attrs and v:
                try:
                    setattr(self, attr, v)
                except Exception as e:
                    failed_to_set[attr] = e
                    
        if failed_to_set:
            print('WARNING! Errors occurred while setting attributes...')
            for attr, error in failed_to_set.items():
                print('\n\t' + attr + ':', error, '\n')
                    
        # commit header
        self.commitHeader()
                  
        
        
    def writeDataByVal(self, df, **kwargs):
        
        pd_origin = pd.to_datetime(0)
        
        varTypes = self.varTypes
        varHandles = self.varHandles
        
        dtypes = df.dtypes.to_dict()
        
        idx_cols = dict(enumerate(df.columns))
        
        writeC = self.spssio.spssSetValueChar
        writeC.argtypes = [c_int, c_double, c_char_p]        
        writeN = self.spssio.spssSetValueNumeric
        writeN.argtypes = [c_int, c_double, c_double]
        
        for row in df.itertuples(index=False, name=None):
            for idx, col in idx_cols.items():
                value = row[idx]
                if pd.notna(value):
                    
                    # string
                    if varTypes[col]:
                        value = value.encode(self.encoding)
                        retcode = writeC(self.fh, varHandles[col], value)
                        if retcode > 0:
                            raise Exception(retcodes.get(retcode))
                        
                    # datetime
                    elif is_datetime64_any_dtype(dtypes[col]):
                        value = (value - pd_origin).total_seconds() + SPSS_ORIGIN_OFFSET
                        retcode = writeN(self.fh, varHandles[col], value)
                        if retcode > 0:
                            raise Exception(retcodes.get(retcode))
                                               
                    # numeric
                    else:
                        retcode = writeN(self.fh, varHandles[col], value)
                        if retcode > 0:
                            raise Exception(retcodes.get(retcode))
                        
            self.commitCaseRecord()
                
            
    
    def writeData(self, df, **kwargs):

        # basic info
        varTypes = self.varTypes
        sysmis = self.sysmis  
        encoding = self.encoding
        
        pd_origin = pd.to_datetime(0)
        
        def get_buffersize(varType):
            return -8 * (varType // -8)
        
        string_padder = ' '.encode(encoding)
        string_cols = {varName: get_buffersize(varType) for varName, varType in varTypes.items() if varType}
                
        endianness = {0:'<', 1: '>'}.get(self.releaseInfo.get("big/little-endian code"), '')

        write_types = {}
        for col, varType in varTypes.items():
            if varType:
                write_types[col] = endianness + 'V' + str(string_cols[col])
            else:
                write_types[col] = endianness + 'd'                
        
        dtypes = df.dtypes.to_dict()

        def finalize(col):
            bufferSize = string_cols.get(col.name)
            if bufferSize:
                return col.apply(lambda x: (
                    x if hasattr(x, 'decode') else (
                        b'' if pd.isna(x) else x.encode(encoding))
                    ).ljust(bufferSize, string_padder))
            elif is_datetime64_any_dtype(dtypes[col.name]):
                return np.nan_to_num((col - pd_origin).dt.total_seconds() + SPSS_ORIGIN_OFFSET, nan=sysmis)
            else:
                return np.nan_to_num(col, nan=sysmis)
                            
        # choose chunksize
        total_records = len(df.index)
        caseSize = self.caseSize     
        mem_to_use = int(psutil.virtual_memory().available * kwargs.get('memory_allocation', 0.1))        
        chunksize = max(1, mem_to_use // caseSize)
        
        # write data
        for i in range(0, total_records, chunksize):
            chunk = df.iloc[i:i+chunksize].transform(finalize).to_records(index=False, column_dtypes=write_types)                                   
            for record in chunk:                      
                caseRec = record.tobytes()
                self._wholeCaseOut(caseRec)




                