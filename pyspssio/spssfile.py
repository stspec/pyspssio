# =============================================================================
# COPYRIGHT NOTICE
# =============================================================================
#
# Copyright (c) 2026 Steven Spector
#
# The pyspssio python package is distributed under the MIT license,
# EXCLUDING files from the IBM I/O Modules for SPSS Statistics
# which are covered under a different license.
#
# License information pertaining to the IBM I/O Modules for SPSS Statistics
# is available in the LICENSE document.
# =============================================================================


import locale as lc
import os
import warnings
from ctypes import (
    POINTER,
    byref,
    c_char_p,
    c_double,
    c_int,
    c_long,
    create_string_buffer,
)
from typing import Optional

from ._runtime import RuntimeState
from .constants import SPSS_MAX_ENCODING
from .errors import warn_or_raise


class SPSSFile:
    """Base class for opening and closing SPSS files"""

    _runtime_state = RuntimeState()

    def __init__(
        self,
        spss_file: str,
        mode: str = "rb",
        unicode: bool = True,
        locale: Optional[str] = None,
    ):

        # initialize SPSS I/O binaries
        SPSSFile._runtime_state.initialize()
        self.spssio = SPSSFile._runtime_state._spssio_runtime

        # basic settings
        self.filename = spss_file
        self.mode = mode[0] + "b"  # always open/close in byte mode

        # functions for opening and closing (always open with utf-8 encoded filenames)
        self._modes = {
            "rb": {
                "open": self.spssio.spssOpenReadU8,
                "close": self.spssio.spssCloseRead,
            },
            "wb": {
                "open": self.spssio.spssOpenWriteU8,
                "close": self.spssio.spssCloseWrite,
            },
            "ab": {
                "open": self.spssio.spssOpenAppendU8,
                "close": self.spssio.spssCloseAppend,
            },
        }

        # get current locale information and set initial encoding
        self.system_locale = lc.setlocale(lc.LC_ALL, "")
        language_code, encoding_category = lc.getlocale()
        self.encoding = "utf-8" if unicode else encoding_category

        # test setting initial locale to obtain encoding
        if locale:
            # force unicode off if locale is specified
            unicode = False
            # set system locale to get locale encoding information
            locale = lc.setlocale(lc.LC_ALL, locale)
            language_code, encoding_category = lc.getlocale()
            # set encoding
            self.encoding = encoding_category
            # reset system locale after getting locale information
            lc.setlocale(lc.LC_ALL, self.system_locale)

        # initialize I/O module in unicode or codepage mode
        self.interface_encoding = unicode

        # set I/O locale and initial encoding
        self.locale = self.set_locale(self.system_locale if not locale else locale)

        # match I/O encoding based on file information for read/append modes
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
        compatible = self.is_compatible_encoding
        if not compatible:
            warnings.warn(
                "File encoding may not be compatible with SPSS I/O interface encoding",
                UnicodeWarning,
            )

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
    def interface_encoding(self) -> int:
        """I/O interface mode (Unicode or code page)

        - 0 = SPSS_ENCODING_CODEPAGE
        - 1 = SPSS_ENCODING_UTF8
        """

        return self.spssio.spssGetInterfaceEncoding()

    @interface_encoding.setter
    def interface_encoding(self, unicode: bool):
        func = self.spssio.spssSetInterfaceEncoding
        func.argtypes = [c_int]
        retcode = func(c_int(int(unicode)))
        warn_or_raise(retcode, func)

    @property
    def file_encoding(self) -> str:
        """File encoding reported by I/O module"""

        func = self.spssio.spssGetFileEncoding
        psz_encoding = create_string_buffer(SPSS_MAX_ENCODING + 1)
        retcode = func(self.fh, psz_encoding)
        warn_or_raise(retcode, func)
        return psz_encoding.value.decode(self.encoding)

    def set_locale(self, locale: str) -> str:
        """Set I/O module to a specific locale"""

        func = self.spssio.spssSetLocale
        func.argtypes = [c_int, c_char_p]
        func.restype = c_char_p
        result = func(lc.LC_ALL, locale.encode(self.encoding))
        if result:
            return result.decode(self.encoding)
        else:
            warnings.warn(
                f"Failed to set locale to: {locale}. Current locale is: {'.'.join(lc.getlocale())}",
                stacklevel=2,
            )
            return ".".join(lc.getlocale())

    @property
    def is_compatible_encoding(self) -> bool:
        """Check encoding compatibility

        From I/O module documentation: "This function determines whether the file's encoding is compatible with the current interface encoding.
        The result value ... will be false when reading a code page file in UTF-8 mode, when reading
        a UTF-8 file in code page mode when reading a code page file encoded in other than the current locale's
        code page, or when reading a file with numbers represented in reverse bit order. If the encoding is
        incompatible, data stored in the file by other applications, particularly Data Entry for Windows, may be
        unreliable."
        """

        func = self.spssio.spssIsCompatibleEncoding
        func.argtypes = [c_int, POINTER(c_int)]
        b_compatible = c_int()
        retcode = func(self.fh, b_compatible)
        warn_or_raise(retcode, func)
        return bool(b_compatible.value)

    def open(self) -> int:
        """Open file

        Returns file handle that is used for most other I/O module functions.

        Notes
        -----
        Filenames are always encoded in UTF-8 regardless of interface mode and locale settings.
        This is to avoid issues where a filename uses special characters that aren't available
        in the encoding defined by the file itself. For example, a Windows-1252 .sav file
        which uses Chinese (or other special multibyte characters) in its filename.
        """

        with open(self.filename, self.mode) as f:
            fh = c_int(f.fileno())
        filename_adjusted = os.path.expanduser(os.path.abspath(self.filename))
        filename_encoded = filename_adjusted.encode("utf-8")
        func = self._modes[self.mode]["open"]
        retcode = func(filename_encoded, byref(fh))
        warn_or_raise(retcode, func)
        return fh

    def close(self):
        """Close file"""

        func = self._modes[self.mode]["close"]
        retcode = func(self.fh)
        warn_or_raise(retcode, func)

    @property
    def compression(self) -> int:
        """Compression level

        - 0 = No compression
        - 1 = SAV
        - 2 = ZSAV
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
    def release_info(self) -> dict:
        """Basic file information

        - release number
        - release subnumber
        - fixpack number
        - machine code
        - floating-point representation code
        - compression scheme code
        - big/little-endian code
        - character representation code
        """

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
        return {item: rel_info_arr[i] for i, item in enumerate(fields)}

    @property
    def var_count(self) -> int:
        """Number of variables"""

        func = self.spssio.spssGetNumberofVariables
        func.argtypes = [c_int, POINTER(c_long)]
        num_vars = c_long()
        retcode = func(self.fh, num_vars)
        warn_or_raise(retcode, func)
        return num_vars.value

    @property
    def case_count(self) -> int:
        """Number of cases"""

        func = self.spssio.spssGetNumberofCases
        func.argtypes = [c_int, POINTER(c_long)]
        num_cases = c_long()
        retcode = func(self.fh, num_cases)
        warn_or_raise(retcode, func)
        return num_cases.value
