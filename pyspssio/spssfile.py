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
import re
import platform
import warnings
import locale as lc

from ctypes import *

from .errors import warn_or_raise
from . import config
from .constants import SPSS_MAX_ENCODING


class SPSSFile(object):
    """Base class for opening and closing SPSS files"""

    def __init__(self, spss_file, mode="rb", unicode=True, locale=None):
        if config.spssio_module is None:
            raise ValueError(
                "Missing spssio module. Set location of module by changing pyspssio.config.spssio_module = path/to/module.ext"
            )

        # basic settings
        self.filename = spss_file
        self.mode = mode[0] + "b"  # always open/close in byte mode

        # load I/O module
        pf = platform.system().lower()

        if pf.startswith("win"):
            loader = WinDLL
            lib_pat = r".*\.dll.*"
        elif pf.startswith("darwin"):
            loader = CDLL
            lib_pat = r".*\.dylib.*"
        else:
            loader = CDLL
            lib_pat = r".*\.so.*"

        path = os.path.dirname(config.spssio_module)
        libs = [os.path.join(path, lib) for lib in sorted(os.listdir(path))]
        libs = [lib for lib in libs if re.fullmatch(lib_pat, lib, re.I)]

        if pf.startswith("win"):
            self._load_libs(libs, loader)
            self.spssio = loader(config.spssio_module)
        else:
            self._load_libs(libs, loader)
            self.spssio = loader(config.spssio_module)

        # functions for opening and closing
        self._modes = {
            "rb": {"open": self.spssio.spssOpenRead, "close": self.spssio.spssCloseRead},
            "wb": {"open": self.spssio.spssOpenWrite, "close": self.spssio.spssCloseWrite},
            "ab": {"open": self.spssio.spssOpenAppend, "close": self.spssio.spssCloseAppend},
        }

        # initialize in unicode or codepage mode
        self.interface_encoding = unicode

        self.system_locale = ".".join(lc.getlocale())
        self.locale = self.set_locale(self.system_locale if not locale else locale)

        # file handle and encoding
        if self.mode in ["rb", "ab"]:
            self.mode = "rb"
            self.fh = self.open()
            self.encoding = self.file_encoding
            self.close()
            self.interface_encoding = self.encoding.lower() in ["utf-8", "utf8"]

        # open file with proper interface encoding and specified mode
        self.mode = mode[0] + "b"
        self.fh = self.open()
        self.encoding = self.file_encoding

        # test encoding compatibility
        compatible = self.is_compatible_encoding()
        if not compatible:
            UnicodeWarning("File encoding may not be compatible with SPSS I/O interface encoding")

        # system missing value for reference to replace with null types
        self.sysmis = self._host_sysmis_val

        # lowest and highest values for missing value ranges
        self.low_value, self.high_value = self._low_high_val

    def __enter__(self):
        return self

    def _exit_cleanup(self):
        self.close()
        self.set_locale(self.system_locale)
        del self.spssio

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self._exit_cleanup()

    def _load_libs(self, libs, loader):
        lib_status = {}
        lib_errors = {}

        try_num = 0
        success = False

        while not success and try_num < len(libs):
            for lib in libs:
                status = True
                try:
                    loader(lib)
                except Exception as e:
                    status = False
                    lib_errors[lib] = e
                finally:
                    lib_status[lib] = status

            success = all(lib_status.values())
            try_num += 1

        return {
            os.path.basename(lib): (status if status else lib_errors[lib])
            for lib, status in lib_status.items()
        }

    @property
    def _low_high_val(self):
        func = self.spssio.spssLowHighVal
        func.argtypes = [POINTER(c_double), POINTER(c_double)]
        lowest = c_double()
        highest = c_double()
        func(lowest, highest)
        return lowest.value, highest.value

    @property
    def _host_sysmis_val(self):
        func = self.spssio.spssHostSysmisVal
        func.argtypes = [POINTER(c_double)]
        sysmis = c_double()
        func(sysmis)
        return sysmis.value

    @property
    def interface_encoding(self):
        """Get or set I/O interface mode

        0 = SPSS_ENCODING_CODEPAGE
        1 = SPSS_ENCODING_UTF8
        """

        return self.spssio.spssGetInterfaceEncoding()

    @interface_encoding.setter
    def interface_encoding(self, unicode):
        func = self.spssio.spssSetInterfaceEncoding
        func.argtypes = [c_int]
        retcode = func(c_int(int(unicode)))
        warn_or_raise(retcode, func)
        return

    @property
    def file_encoding(self):
        """File encoding reported by I/O module"""

        func = self.spssio.spssGetFileEncoding
        psz_encoding = create_string_buffer(SPSS_MAX_ENCODING + 1)
        retcode = func(self.fh, psz_encoding)
        warn_or_raise(retcode, func)
        return psz_encoding.value.decode("utf-8")

    def set_locale(self, locale):
        """Set I/O module with a specific locale"""

        func = self.spssio.spssSetLocale
        func.argtypes = [c_int, c_char_p]
        func.restype = c_char_p
        result = func(lc.LC_ALL, locale.encode("utf-8"))
        if result:
            return result.decode("utf-8")
        else:
            warnings.warn(
                "Failed to set locale to: "
                + locale
                + ". "
                + "Current locale is: "
                + ".".join(lc.getlocale()),
                stacklevel=2,
            )
            return ".".join(lc.getlocale())

    def is_compatible_encoding(self):
        """Check encoding compatibility"""

        func = self.spssio.spssIsCompatibleEncoding
        func.argtypes = [c_int, POINTER(c_int)]
        b_compatible = c_int()
        retcode = func(self.fh, b_compatible)
        warn_or_raise(retcode, func)
        return b_compatible.value

    def open(self):
        """Open file"""

        with open(self.filename, self.mode) as f:
            fh = c_int(f.fileno())
        filename_adjusted = os.path.expanduser(os.path.abspath(self.filename)).encode("utf-8")
        func = self._modes[self.mode]["open"]
        retcode = func(filename_adjusted, byref(fh))
        warn_or_raise(retcode, func)
        return fh

    def close(self):
        """Close file"""

        func = self._modes[self.mode]["close"]
        retcode = func(self.fh)
        warn_or_raise(retcode, func)

    @property
    def compression(self):
        """Get or set compression level

        0 = No compression
        1 = SAV
        2 = ZSAV
        """

        func = self.spssio.spssGetCompression
        func.argtypes = [c_int, POINTER(c_int)]
        comp_switch = c_int()
        retcode = func(self.fh, comp_switch)
        warn_or_raise(retcode, func)
        return comp_switch.value

    @compression.setter
    def compression(self, comp_switch=1):
        func = self.spssio.spssSetCompression
        retcode = func(self.fh, c_int(comp_switch))
        warn_or_raise(retcode, func)

    @property
    def release_info(self):
        """Basic file information"""

        fields = [
            "release number",
            "release subnumber",
            "fixpack number",
            "machine code",
            "floating-point representation code",
            "compression scheme code",
            "big/little-endian code",
            "character representation code",
        ]
        rel_info_arr = (c_int * len(fields))()
        func = self.spssio.spssGetReleaseInfo
        retcode = func(self.fh, rel_info_arr)
        warn_or_raise(retcode, func)
        return dict([(item, rel_info_arr[i]) for i, item in enumerate(fields)])

    @property
    def var_count(self):
        """Number of variables"""

        func = self.spssio.spssGetNumberofVariables
        func.argtypes = [c_int, POINTER(c_long)]
        num_vars = c_long()
        retcode = func(self.fh, num_vars)
        warn_or_raise(retcode, func)
        return num_vars.value

    @property
    def case_count(self):
        """Number of cases"""

        func = self.spssio.spssGetNumberofCases
        func.argtypes = [c_int, POINTER(c_long)]
        num_cases = c_long()
        retcode = func(self.fh, num_cases)
        warn_or_raise(retcode, func)
        return num_cases.value
