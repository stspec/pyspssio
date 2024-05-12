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

import sys
import argparse
import inspect

from . import user_functions


def parse_arguments(func):
    """Helper function for reading a method signature and parsing command lind arguments"""

    parser = argparse.ArgumentParser()
    for parammeter in inspect.signature(func).parameters:
        parser.add_argument("--" + parammeter)
    args = parser.parse_args()
    return vars(args)


def main():
    """Main CLI caller

    First argument should be name of pyspssio user function (ex. read_sav)
    Remaining arguments should be function inputs

    Examples
    --------
    >>> pyspssio read_sav --spss_file "data.sav"

    """

    func = getattr(user_functions, sys.argv[1])
    sys.argv = sys.argv[0:1] + sys.argv[2:]
    kwargs = parse_arguments(func)
    return func(**kwargs)
