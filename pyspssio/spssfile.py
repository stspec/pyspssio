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
import threading
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
from .errors import SPSSWarning, warn_or_raise


class SPSSFile:
    """Base class for opening and closing SPSS files"""

    _runtime_state = None
    _runtime_state_lock = threading.Lock()

    def __init__(
        self,
        spss_file: str,
        mode: str = "rb",
        unicode: Optional[bool] = None,
        locale: Optional[str] = None,
    ):

        # create shared runtime state on first use
        # to avoid initializing eagerly on module import
        if SPSSFile._runtime_state is None:
            with SPSSFile._runtime_state_lock:
                if SPSSFile._runtime_state is None:
                    SPSSFile._runtime_state = RuntimeState()

        # initialize SPSS I/O binaries
        SPSSFile._runtime_state.initialize()
        self.spssio = SPSSFile._runtime_state._spssio_runtime
        self.system_locale = lc.setlocale(lc.LC_ALL, "")

        # set user inputs
        self.filename = spss_file
        self._mode = mode.lower()[0] + "b"
        self._unicode = unicode
        self._locale = locale

        # assign user inputs to active state
        self.mode = self._mode

        if self._locale:
            self.unicode = False
        elif self._unicode is None:
            self.unicode = True
        else:
            self.unicode = self._unicode

        self._use_locale = self._locale or self.system_locale

        # set assumed encodings
        self.interface_encoding = self.unicode
        if self.unicode:
            self.encoding = "utf-8"
            self.locale = None
        else:
            self.encoding = self._get_locale_encoding(self._use_locale)
            self.locale = self.set_locale(self._use_locale)

        # get details about I/O encoding based on file information
        # for read/append modes then reset active mode
        if self.mode in ["rb", "ab"]:
            self.mode = "rb"
            self.fh = self.open()
            _detected_unicode = self.file_encoding.lower() in ("utf-8", "utf8")
            self.close()
            self.mode = self._mode

            # set detected encodings
            if _detected_unicode:
                self.unicode = True
                self.interface_encoding = True
                self.locale = None
            else:
                self.unicode = False
                self.interface_encoding = False
                self.locale = self.set_locale(self._use_locale)

        # open file with proper interface encoding and specified mode
        self.fh = self.open()
        self.encoding = self.file_encoding

        # test encoding compatibility for read/append modes only
        if self.mode in ("rb", "ab") and not self.is_compatible_encoding:
            warnings.warn(
                "File encoding may not be compatible with SPSS I/O interface encoding",
                SPSSWarning,
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

    def _get_locale_encoding(self, locale: Optional[str] = None) -> str:
        """Get encoding category of specified locale.
        Use locale = None or "" to return the system locale encoding.
        """
        try:
            # get specified locale encoding
            locale = locale or self.system_locale
            locale = lc.setlocale(lc.LC_ALL, locale)
            _, encoding_category = lc.getlocale()
            # return encoding
            return encoding_category

        finally:
            # reset system locale after getting locale information
            lc.setlocale(lc.LC_ALL, self.system_locale)

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
            current_locale = ".".join(lc.getlocale())
            warnings.warn(
                f"Failed to set locale to: {locale}. Current locale is: {current_locale}",
                stacklevel=2,
            )
            return current_locale

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

        if self.mode == "rb":
            func = self.spssio.spssOpenReadU8
        elif self.mode == "wb":
            func = self.spssio.spssOpenWriteU8
        elif self.mode == "ab":
            func = self.spssio.spssOpenAppendU8

        with open(self.filename, self.mode) as f:
            fh = c_int(f.fileno())
        filename_adjusted = os.path.expanduser(os.path.abspath(self.filename))
        filename_encoded = filename_adjusted.encode("utf-8")
        retcode = func(filename_encoded, byref(fh))
        warn_or_raise(retcode, func)
        return fh

    def close(self):
        """Close file"""

        if self.mode == "rb":
            func = self.spssio.spssCloseRead
        elif self.mode == "wb":
            func = self.spssio.spssCloseWrite
        elif self.mode == "ab":
            func = self.spssio.spssCloseAppend

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
