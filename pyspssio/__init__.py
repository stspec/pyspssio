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

from . import config
from .constants import *
from .errors import SPSSError, SPSSWarning
from .header import Header
from .reader import Reader
from .spssfile import SPSSFile
from .user_functions import (
    append_sav,
    read_metadata,
    read_sav,
    write_sav,
)
from .writer import Writer

try:
    from importlib.metadata import version

    __version__ = version("pyspssio")
except ImportError:
    __version__ = "unknown"
