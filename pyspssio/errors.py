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

import warnings
from . import config
from .constants import *

# fmt: off

class SPSSWarning(Warning):
    """Capture I/O module warnings"""

class SPSSError(Exception):
    """Capture I/O module errors"""

spss_warn_error = {
    SPSS_OK:                         (None, "No error"),
    SPSS_FILE_OERROR:                (SPSSError, "SPSS_FILE_OERROR: Error opening new file for output"),
    SPSS_FILE_WERROR:                (SPSSError, "SPSS_FILE_WERROR: File write error"),
    SPSS_FILE_RERROR:                (SPSSError, "SPSS_FILE_RERROR: Error reading file"),
    SPSS_FITAB_FULL:                 (SPSSError, "SPSS_FITAB_FULL: File table full (too many open IBM SPSS Statistics data files)"),
    SPSS_INVALID_HANDLE:             (SPSSError, "SPSS_INVALID_HANDLE: The file handle is not valid"),
    SPSS_INVALID_FILE:               (SPSSError, "SPSS_INVALID_FILE: The file is not a valid IBM SPSS Statistics data file"),
    SPSS_NO_MEMORY:                  (SPSSError, "SPSS_NO_MEMORY: Insufficient memory"),
    SPSS_OPEN_RDMODE:                (SPSSError, "SPSS_OPEN_RDMODE: File is open for reading, not writing"),
    SPSS_OPEN_WRMODE:                (SPSSError, "SPSS_OPEN_WRMODE: File is open for writing, not reading"),
    SPSS_INVALID_VARNAME:            (SPSSError, "SPSS_INVALID_VARNAME: The variable name is not valid"),
    SPSS_DICT_EMPTY:                 (SPSSError, "SPSS_DICT_EMPTY: No variables defined in the dictionary."),
    SPSS_VAR_NOTFOUND:               (SPSSError, "SPSS_VAR_NOTFOUND: A variable with the given name does not exist"),
    SPSS_DUP_VAR:                    (SPSSError, "SPSS_DUP_VAR: There is already a variable with the same name"),
    SPSS_NUME_EXP:                   (SPSSError, "SPSS_NUME_EXP: At least one of the variables is not numeric."),
    SPSS_STR_EXP:                    (SPSSError, "SPSS_STR_EXP: At least one of the variables is numeric."),
    SPSS_SHORTSTR_EXP:               (SPSSError, "SPSS_SHORTSTR_EXP: At least one of the variables is a long string (length < 8)."),
    SPSS_INVALID_VARTYPE:            (SPSSError, "SPSS_INVALID_VARTYPE: Invalid length code (varLength is negative or exceeds 32767)"),
    SPSS_INVALID_MISSFOR:            (SPSSError, "SPSS_INVALID_MISSFOR: Invalid missing values specification (missingFormat is invalid or the lower limit of range is greater than the upper limit)"),
    SPSS_INVALID_COMPSW:             (SPSSError, "SPSS_INVALID_COMPSW: Invalid compression switch (other than 0, 1 or 2)"),
    SPSS_INVALID_PRFOR:              (SPSSError, "SPSS_INVALID_PRFOR: The print format specification is invalid or is incompatible with the variable type"),
    SPSS_INVALID_WRFOR:              (SPSSError, "SPSS_INVALID_WRFOR: The write format specification is invalid or is incompatible with the variable type"),
    SPSS_INVALID_DATE:               (SPSSError, "SPSS_INVALID_DATE: The date value (spssDate) is negative"),
    SPSS_INVALID_TIME:               (SPSSError, "SPSS_INVALID_TIME: Invalid time"),
    SPSS_NO_VARIABLES:               (SPSSError, "SPSS_NO_VARIABLES: Number of variables (numVars) is zero or negative."),
    SPSS_MIXED_TYPES:                (SPSSError, "SPSS_MIXED_TYPES: "),
    SPSS_DUP_VALUE:                  (SPSSError, "SPSS_DUP_VALUE: The list of values contains duplicates."),
    SPSS_INVALID_CASEWGT:            (SPSSError, "SPSS_INVALID_CASEWGT: The given case weight variable is invalid. This error signals an internal"),
    SPSS_INCOMPATIBLE_DICT:          (SPSSError, "SPSS_INCOMPATIBLE_DICT: There is no Windows code page equivalent for the file's encoding"),
    SPSS_DICT_COMMIT:                (SPSSError, "SPSS_DICT_COMMIT: Dictionary has already been written with spssCommitHeader"),
    SPSS_DICT_NOTCOMMIT:             (SPSSError, "SPSS_DICT_NOTCOMMIT: Dictionary of the output file has not yet been written with spssCommitHeader"),
    SPSS_NO_TYPE2:                   (SPSSError, "SPSS_NO_TYPE2: File is not a valid IBM SPSS Statistics data file (no type 2 record)"),
    SPSS_NO_TYPE73:                  (SPSSWarning, "SPSS_NO_TYPE73: There is no type 7, subtype 3 record present. This code should be regarded as a warning even though it is positive. Files without this record are valid."),
    SPSS_INVALID_DATEINFO:           (SPSSError, "SPSS_INVALID_DATEINFO: The date variable information is invalid"),
    SPSS_NO_TYPE999:                 (SPSSError, "SPSS_NO_TYPE999: File is not a valid IBM SPSS Statistics data file (missing type 999 record)"),
    SPSS_EXC_STRVALUE:               (SPSSError, "SPSS_EXC_STRVALUE: At least one value is longer than the length of the variable."),
    SPSS_CANNOT_FREE:                (SPSSError, "SPSS_CANNOT_FREE: Cannot deallocate the memory, probably due to invalid arguments."),
    SPSS_BUFFER_SHORT:               (SPSSError, "SPSS_BUFFER_SHORT: Buffer value is too short to hold the value."),
    SPSS_INVALID_CASE:               (SPSSError, "SPSS_INVALID_CASE: Current case is not valid. This may be because no spssReadCaseRecord calls"),
    SPSS_INTERNAL_VLABS:             (SPSSError, "SPSS_INTERNAL_VLABS: Internal data structures of the I/O Module are invalid. This signals an error in the I/O Module."),
    SPSS_INCOMPAT_APPEND:            (SPSSError, "SPSS_INCOMPAT_APPEND: File created on an incompatible system."),
    SPSS_INTERNAL_D_A:               (SPSSError, "SPSS_INTERNAL_D_A: "),
    SPSS_FILE_BADTEMP:               (SPSSError, "SPSS_FILE_BADTEMP: Cannot open or write to temporary file."),
    SPSS_DEW_NOFIRST:                (SPSSError, "SPSS_DEW_NOFIRST: spssSetDEWFirst was never called"),
    SPSS_INVALID_MEASURELEVEL:       (SPSSError, "SPSS_INVALID_MEASURELEVEL: measureLevel is not in the legal range, or it is SPSS_MLVL_RAT and the variable is a string variable."),
    SPSS_INVALID_7SUBTYPE:           (SPSSError, "SPSS_INVALID_7SUBTYPE: Parameter subtype not between 1 and MAX7SUBTYPE."),
    SPSS_INVALID_VARHANDLE:          (SPSSError, "SPSS_INVALID_VARHANDLE: "),
    SPSS_INVALID_ENCODING:           (SPSSError, "SPSS_INVALID_ENCODING: The specified encoding is not valid."),
    SPSS_FILES_OPEN:                 (SPSSError, "SPSS_FILES_OPEN: IBM SPSS Statistics files are open."),
    SPSS_INVALID_MRSETDEF:           (SPSSError, "SPSS_INVALID_MRSETDEF: Existing multiple-response set definitions are invalid."),
    SPSS_INVALID_MRSETNAME:          (SPSSError, "SPSS_INVALID_MRSETNAME: The multiple-response set name is invalid."),
    SPSS_DUP_MRSETNAME:              (SPSSError, "SPSS_DUP_MRSETNAME: The multiple-response set name is a duplicate."),
    SPSS_BAD_EXTENSION:              (SPSSError, "SPSS_BAD_EXTENSION: "),
    SPSS_INVALID_EXTENDEDSTRING:     (SPSSError, "SPSS_INVALID_EXTENDEDSTRING: "),
    SPSS_INVALID_ATTRNAME:           (SPSSError, "SPSS_INVALID_ATTRNAME: Lexically invalid attribute name."),
    SPSS_INVALID_ATTRDEF:            (SPSSError, "SPSS_INVALID_ATTRDEF: Missing name, missing text, or invalid subscript."),
    SPSS_INVALID_MRSETINDEX:         (SPSSError, "SPSS_INVALID_MRSETINDEX: The index is out of range."),
    SPSS_INVALID_VARSETDEF:          (SPSSError, "SPSS_INVALID_VARSETDEF: "),
    SPSS_INVALID_ROLE:               (SPSSError, "SPSS_INVALID_ROLE: Invalid role value"),
    SPSS_EXC_LEN64:                  (SPSSWarning, "SPSS_EXC_LEN64: Label length exceeds 64; truncated and used"),
    SPSS_EXC_LEN120:                 (SPSSWarning, "SPSS_EXC_LEN120: Label length exceeds 120; truncated and used"),
    SPSS_EXC_VARLABEL:               (SPSSWarning, "SPSS_EXC_VARLABEL: "),
    SPSS_EXC_LEN60:                  (SPSSWarning, "SPSS_EXC_LEN60: Label length exceeds 60; truncated and used"),
    SPSS_EXC_VALLABEL:               (SPSSWarning, "SPSS_EXC_VALLABEL: "),
    SPSS_FILE_END:                   (SPSSWarning, "SPSS_FILE_END: End of the file reached; no more cases"),
    SPSS_NO_VARSETS:                 (SPSSWarning, "SPSS_NO_VARSETS: There is no variable sets information in the file"),
    SPSS_EMPTY_VARSETS:              (SPSSWarning, "SPSS_EMPTY_VARSETS: The variable sets information is empty"),
    SPSS_NO_LABELS:                  (SPSSWarning, "SPSS_NO_LABELS: Number of labels (numLabels) is zero or negative."),
    SPSS_NO_LABEL:                   (SPSSWarning, "SPSS_NO_LABEL: There is no label for the given value"),
    SPSS_NO_CASEWGT:                 (SPSSWarning, "SPSS_NO_CASEWGT: A case weight variable has not been defined for this file"),
    SPSS_NO_DATEINFO:                (SPSSWarning, "SPSS_NO_DATEINFO: There is no Trends date variable information in the file"),
    SPSS_NO_MULTRESP:                (SPSSWarning, "SPSS_NO_MULTRESP: No definitions on the file"),
    SPSS_EMPTY_MULTRESP:             (SPSSWarning, "SPSS_EMPTY_MULTRESP: The string contains no definitions"),
    SPSS_NO_DEW:                     (SPSSWarning, "SPSS_NO_DEW: File contains no DEW information"),
    SPSS_EMPTY_DEW:                  (SPSSWarning, "SPSS_EMPTY_DEW: Zero bytes to be written")
}

def warn_or_raise(retcode, func, *args):
    """Function to warn warnings and raise exceptions from I/O module return codes"""

    if retcode == SPSS_OK:
        return

    retcode_type, message = spss_warn_error.get(retcode, (SPSSError, "Return code not recognized"))

    info = ", ".join(map(str, args)) if args else "None"

    if func is not None:
        message = f"[{func.__name__}] {message} > {info}"

    warn_error = retcode_type(message)

    if isinstance(warn_error, SPSSWarning) and config.show_warnings:
        warnings.warn(warn_error, stacklevel=2)
    elif isinstance(warn_error, SPSSError):
        raise warn_error
