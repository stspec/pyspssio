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

import os
import platform
import warnings

from . import config
from .constants import *
from .errors import SPSSError, SPSSWarning
from .header import Header
from .reader import Reader
from .spssfile import SPSSFile
from .user_functions import Any as Any
from .user_functions import DataFrame as DataFrame
from .user_functions import Generator as Generator
from .user_functions import Reader as Reader
from .user_functions import Writer as Writer
from .user_functions import append_sav as append_sav
from .user_functions import read_metadata as read_metadata
from .user_functions import read_sav as read_sav
from .user_functions import write_sav as write_sav
from .writer import Writer

try:
    from importlib.metadata import version

    __version__ = version("pyspssio")
except ImportError:
    __version__ = "unknown"

module_path = os.path.dirname(__file__)
source_root = os.path.dirname(module_path)

pf_system = platform.system().lower()

# Windows 64
if pf_system.startswith("win"):
    spssio_folder = "win64"
    spssio_module = "spssio64.dll"

# MacOS
elif pf_system.startswith("darwin"):
    spssio_folder = "macos"
    spssio_module = "libspssdio.dylib"

# Linux
elif pf_system.startswith("lin"):
    spssio_folder = "lin64"
    spssio_module = "libspssdio.so.1"

try:
    config.spssio_module = os.path.join(
        module_path, "spssio", spssio_folder, spssio_module
    )
except Exception as err:
    warnings.warn(err, stacklevel=2)
