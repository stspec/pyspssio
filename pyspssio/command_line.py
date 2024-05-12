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
from inspect import signature, getmembers, isfunction

from . import user_functions


funcs = {}
for func_name, func in getmembers(user_functions, isfunction):
    parser = argparse.ArgumentParser()
    func_help = ""
    for name, parameter in signature(func).parameters.items():
        parser.add_argument("--" + name)
        func_help += "\n - " + str(parameter)

    funcs[func_name] = {"func": func, "parser": parser, "help": func_help.strip("\n")}

help_message = f'''
### Usage ###

pyspssio <function> --arg1 arg1 --arg2 arg2

### Functions ###

{'\n'.join(' - ' + func_name for func_name in funcs.keys())}

### Function Signatures ###

{'\n\n'.join(name + '\n' + func['help'] for name, func in funcs.items())}

'''


def call_function(func_name):
    """Helper function for calling function"""

    func_info = funcs[func_name]
    parser = func_info["parser"]
    func = func_info["func"]
    kwargs = vars(parser.parse_args())

    try:
        return func(**kwargs)
    except Exception as err:
        print(err, kwargs, func_info["help"], sep="\n\n")


def main():
    """Main CLI caller

    First argument should be name of pyspssio user function (ex. read_sav)
    Remaining arguments should be function inputs

    Examples
    --------
    >>> pyspssio read_sav --spss_file "data.sav"

    """

    if len(sys.argv) <= 1:
        print(help_message)
        return

    func_name = sys.argv[1]
    sys.argv = sys.argv[0:1] + sys.argv[2:]
    return call_function(func_name)
