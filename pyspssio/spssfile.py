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
import platform
import locale
import warnings

from ctypes import *

import config
from constants import retcodes, max_lengths




class SpssFile(object):
        
    def __init__(self, spss_file, mode='rb', unicode=True, set_locale=None):
        if config.spssio_module is None:
            raise ValueError('Missing spssio module. Set location of module by changing pyspssio.config.spssio_module = path/to/module.ext')
            
        # basic settings
        self.filename = spss_file
        self.mode = mode[0] + 'b'   # always open/close in byte mode        
              
        # load module        
        def load_libs(libs, loader):
            loaded_libs = []
            for lib in libs:
                try:
                    loaded_libs.append(loader(lib))
                except:
                    pass
            return loaded_libs
        
        loader = WinDLL if platform.system().lower().startswith('win') else CDLL
        path = os.path.dirname(config.spssio_module)
        libs = [os.path.join(path, lib) for lib in sorted(os.listdir(path))]
        loaded_libs = load_libs(libs, loader)
        loaded_libs = load_libs(libs, loader)
        self.spssio = loader(config.spssio_module)
        
        """ 
        modes
        ------
        write copy not implemented, but write function allows passing metadata object
        append mode does not allow modifying data dictionary, so be careful with string variables as width cannot be changed
        """        
        self._modes = {'rb': {'open': self.spssio.spssOpenReadU8, 'close': self.spssio.spssCloseRead},        # read
                       'wb': {'open': self.spssio.spssOpenWriteU8, 'close': self.spssio.spssCloseWrite},      # write
                       'ab': {'open': self.spssio.spssOpenAppendU8, 'close': self.spssio.spssCloseAppend}     # append
                       }         
        
                
        # initialize in unicode or codepage mode       
        self.interfaceEncoding = unicode
        
        self.system_locale = '.'.join(locale.getlocale())
        self.locale = self.setLocale(self.system_locale if not set_locale else set_locale)
                      
        # file handle and encoding
        if self.mode in ['rb','ab']:
            self.mode = 'rb'
            self.fh = self.openSPSS()    
            self.encoding = self.fileEncoding
            self.closeSPSS()
            self.interfaceEncoding = (self.encoding.lower() in ['utf-8', 'utf8'])
                    
        # open file with proper interface encoding and specified mode
        self.mode = mode[0] + 'b'
        self.fh = self.openSPSS()
        self.encoding = self.fileEncoding
        
        # test encoding compatibility
        compatible = retcodes.get(self.isCompatibleEncoding())
        if not compatible:
            UnicodeWarning("File encoding may not be compatible with SPSS I/O interface encoding")
        
        # system missing value for reference to replace with null types
        self.sysmis = self._hostSysmisVal()
               
    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.closeSPSS()
        self.setLocale(self.system_locale)
        del self.spssio
        
    def _hostSysmisVal(self):
        func = self.spssio.spssHostSysmisVal
        func.argtypes = [POINTER(c_double)]        
        sysmis = c_double()
        func(sysmis)
        return sysmis.value
     
    @property
    def interfaceEncoding(self):   
        """Get or set I/O interface mode

        0 = SPSS_ENCODING_CODEPAGE
        1 = SPSS_ENCODING_UTF8
        """

        return self.spssio.spssGetInterfaceEncoding()
    
    @interfaceEncoding.setter
    def interfaceEncoding(self, unicode):
        func = self.spssio.spssSetInterfaceEncoding
        func.argtypes = [c_int]
        retcode = func(c_int(int(unicode)))
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
        return
    
    @property
    def fileEncoding(self):
        func = self.spssio.spssGetFileEncoding
        pszEncoding = create_string_buffer(max_lengths['SPSS_MAX_ENCODING'] + 1)
        retcode = func(self.fh, pszEncoding)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
        return pszEncoding.value.decode('utf-8')
    
    def setLocale(self, set_locale):
        func = self.spssio.spssSetLocale
        func.argtypes = [c_int, c_char_p]
        func.restype = c_char_p
        result = func(locale.LC_ALL, set_locale.encode('utf-8'))
        if result:
            return result.decode('utf-8')
        else:
            warnings.warn('Failed to set locale to: ' + set_locale + '. ' + 
                          'Current locale is: ' + '.'.join(locale.getlocale()), 
                          stacklevel=2)
            return '.'.join(locale.getlocale())
    
    def isCompatibleEncoding(self):
        func = self.spssio.spssIsCompatibleEncoding
        func.argtypes = [c_int, POINTER(c_int)]
        bCompatible = c_int()
        return func(self.fh, bCompatible)
    
    def openSPSS(self):
        with open(self.filename, self.mode) as f:
            fh = c_int(f.fileno())
        filename_adjusted = os.path.expanduser(os.path.abspath(self.filename)).encode('utf-8')
        func = self._modes[self.mode]['open']
        retcode = func(filename_adjusted, byref(fh))
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
        return fh           
    
    def closeSPSS(self):
        func = self._modes[self.mode]['close']
        retcode = func(self.fh)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
     
    @property
    def compression(self):
        """Get or set compression level

        0 = No compression
        1 = SAV
        2 = ZSAV
        """

        func = self.spssio.spssGetCompression
        func.argtypes = [c_int, POINTER(c_int)] 
        compSwitch = c_int()
        retcode = func(self.fh, compSwitch)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
        return compSwitch.value
    
    @compression.setter
    def compression(self, compSwitch=1):        
        retcode = self.spssio.spssSetCompression(self.fh, c_int(compSwitch))
        if retcode > 0:
            raise ValueError(retcodes.get(retcode))    
    
    @property   
    def releaseInfo(self):
         relInfo = ["release number", "release subnumber", "fixpack number",
                    "machine code", "floating-point representation code",
                    "compression scheme code", "big/little-endian code",
                    "character representation code"]
         relInfoArr = (c_int * len(relInfo))()
         retcode = self.spssio.spssGetReleaseInfo(self.fh, relInfoArr)
         retcode = retcodes.get(retcode)
         if retcode == 'SPSS_INVALID_HANDLE':
             raise Exception(retcode)
         return dict([(item, relInfoArr[i]) for i, item in enumerate(relInfo)])
     
    @property
    def varCount(self):
        func = self.spssio.spssGetNumberofVariables
        func.argtypes = [c_int, POINTER(c_long)]
        numVars = c_long()
        retcode = func(self.fh, numVars)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
        else:
            return numVars.value
        
    @property
    def caseCount(self):
        func = self.spssio.spssGetNumberofCases
        func.argtypes = [c_int, POINTER(c_long)]
        numofCases = c_long()
        retcode = func(self.fh, numofCases)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
        else:
            return numofCases.value    
       

           
                
                 