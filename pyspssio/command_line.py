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
import ast
import json
import argparse
from inspect import signature, isfunction, Parameter
from pandas import DataFrame

from . import user_functions


HELP_MESSAGE = """
Usage:
pyspssio <function> --arg1 arg1 --arg2 arg2

Functions:
 - read_sav
 - read_metadata
 - write_sav
 - append_sav

"""


def boolean(value):
    """Safely convert input value to boolean"""

    if isinstance(value, str):
        value = value.title()
    return bool(ast.literal_eval(value))


def dictionary(value):
    """Safely convert input value to dictionary"""

    if isinstance(value, str):
        value = json.loads(value)
    return dict(value)


def dataframe(value):
    """Safely convert input value to pandas DataFrame"""

    # Attempt to interpret string input as python object
    # before passing to pandas DataFrame constructor
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception as err_json:
            print(err_json, file=sys.stderr)
            try:
                value = ast.literal_eval(value)
            except Exception as err_eval:
                print(err_eval, file=sys.stderr)

    return DataFrame(value)


def get_parser(func):
    """Retrieve function parser for CLI"""

    parser = argparse.ArgumentParser(formatter_class=argparse.MetavarTypeHelpFormatter)
    parameters = signature(func).parameters

    for name, parameter in parameters.items():
        default = None if parameter.default == Parameter.empty else parameter.default

        if name == "df":
            parser.add_argument("--" + name, type=dataframe)
        elif name == "usecols":
            parser.add_argument("--" + name, type=str, nargs="*")
        elif name == "kwargs":
            continue
        elif parameter.annotation in [str, int, float]:
            parser.add_argument("--" + name, type=parameter.annotation, default=default)
        elif parameter.annotation == bool:
            parser.add_argument("--" + name, type=boolean, default=default)
        elif parameter.annotation == dict:
            parser.add_argument("--" + name, type=dictionary, default=default)
        else:
            parser.add_argument("--" + name, type=str, default=default)

    return parser


def call_function(func_name):
    """Helper function for calling function"""

    func = getattr(user_functions, func_name)

    if not isfunction(func):
        print(f"{HELP_MESSAGE}\nFunction not recognized: {func_name}\n", file=sys.stderr)
        return None

    parser = get_parser(func)
    kwargs = vars(parser.parse_args())

    try:
        return func(**kwargs)
    except Exception as err:
        print(f"\n{parser.format_help()}\n\n{kwargs}\n\n{err}\n", file=sys.stderr)
        return None


def main():
    """Main CLI caller

    First argument should be name of pyspssio user function (ex. read_sav).
    Remaining arguments should be function inputs.

    Examples
    --------
    >>> pyspssio read_sav --spss_file "data.sav"

    """

    if len(sys.argv) <= 1:
        print(HELP_MESSAGE, file=sys.stdout)
        return None

    func_name = sys.argv[1]
    if func_name.lower() in ["-h", "--help"]:
        print(HELP_MESSAGE, file=sys.stdout)
        return None

    sys.argv = sys.argv[0:1] + sys.argv[2:]
    return call_function(func_name)
