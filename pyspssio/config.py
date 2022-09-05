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

from .constants import *
from .constants_map import *

# fmt: off

show_warnings = False

# must set spssio filepath before using
spssio_module = None

# default formats
default_numeric_format  = (5, 8, 2)         # F8.2
default_date_format     = (20, 11, 0)       # DATE11
default_time_format     = (21, 8, 0)        # TIME8
default_datetime_format = (22, 20, 0)       # DATETIME20

# date & datetime formats to convert
spss_datetime_formats_to_convert = spss_date_formats + spss_datetime_formats
spss_time_formats_to_convert = spss_time_formats
