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
from inspect import signature, getmembers, isfunction, Parameter
from pandas import DataFrame

from . import user_functions


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
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            try:
                value = ast.literal_eval(value.title())
            except Exception:
                pass

    return DataFrame(value)


funcs = {}
for func_name, func in getmembers(user_functions, isfunction):
    parser = argparse.ArgumentParser(formatter_class=argparse.MetavarTypeHelpFormatter)
    parameters = signature(func).parameters
    for name, parameter in parameters.items():
        default = None if parameter.default == Parameter.empty else parameter.default
        if parameter.annotation in [str, int, float]:
            parser.add_argument("--" + name, type=parameter.annotation, default=default)
        elif parameter.annotation == bool:
            parser.add_argument("--" + name, type=boolean, default=default)
        elif parameter.annotation == dict:
            parser.add_argument("--" + name, type=dictionary, default=default)
        elif name == "df":
            parser.add_argument("--" + name, type=dataframe)
        elif name == "usecols":
            parser.add_argument("--" + name, type=str, nargs="*")
        elif name == "kwargs":
            continue
        else:
            parser.add_argument("--" + name, type=str, default=default)

    funcs[func_name] = {"func": func, "parser": parser, "help": parser.format_help()}

help_message = f'''
Usage:
pyspssio <function> --arg1 arg1 --arg2 arg2

Functions:
{'\n'.join(' - ' + func_name for func_name in funcs)}

'''


def call_function(func_name):
    """Helper function for calling function"""

    try:
        func_info = funcs[func_name]
    except KeyError:
        sys.stderr.write(f"{help_message}\nFunction not recognized: {func_name}\n")
        return None

    parser = func_info["parser"]
    func = func_info["func"]
    kwargs = vars(parser.parse_args())

    try:
        return func(**kwargs)
    except Exception as err:
        sys.stderr.write(f'\n{func_info["help"]}\n\n{kwargs}\n\n{err}\n')
        return None


def main():
    """Main CLI caller

    First argument should be name of pyspssio user function (ex. read_sav)
    Remaining arguments should be function inputs

    Examples
    --------
    >>> pyspssio read_sav --spss_file "data.sav"

    """

    if len(sys.argv) <= 1:
        sys.stdout.write(help_message)
        return None

    func_name = sys.argv[1]
    if func_name.lower() in ["-h", "--help"]:
        sys.stdout.write(help_message)
        return None

    sys.argv = sys.argv[0:1] + sys.argv[2:]
    return call_function(func_name)
