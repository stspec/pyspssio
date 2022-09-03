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

# fmt: off

# max string lengths
SPSS_MAX_VARNAME        = 64
SPSS_MAX_SHORTVARNAME   = 8
SPSS_MAX_SHORTSTRING    = 8
SPSS_MAX_IDSTRING       = 64
SPSS_MAX_LONGSTRING     = 32767
SPSS_MAX_VALLABEL       = 120
SPSS_MAX_VARLABEL       = 256
SPSS_MAX_ENCODING       = 64
SPSS_MAX_7SUBTYPE       = 40
SPSS_MAX_PASSWORD       = 10

# user missing value types
SPSS_NO_MISSVAL         = 0
SPSS_ONE_MISSVAL        = 1
SPSS_TWO_MISSVAL        = 2
SPSS_THREE_MISSVAL      = 3
SPSS_MISS_RANGE         = -2
SPSS_MISS_RANGEANDVAL   = -3

# formats
SPSS_FMT_A              = 1     # Alphanumeric
SPSS_FMT_AHEX           = 2     # Alphanumeric hexadecimal
SPSS_FMT_COMMA          = 3     # F Format with commas
SPSS_FMT_DOLLAR         = 4     # Commas and floating dollar sign
SPSS_FMT_F              = 5     # Default Numeric Format
SPSS_FMT_IB             = 6     # Integer binary
SPSS_FMT_PIBHEX         = 7     # Positive integer binary - hex
SPSS_FMT_P              = 8     # Packed decimal
SPSS_FMT_PIB            = 9     # Positive integer binary unsigned
SPSS_FMT_PK             = 10    # Positive integer binary unsigned
SPSS_FMT_RB             = 11    # Floating point binary
SPSS_FMT_RBHEX          = 12    # Floating point binary hex
SPSS_FMT_Z              = 15    # Zoned decimal
SPSS_FMT_N              = 16    # N Format- unsigned with leading 0s
SPSS_FMT_E              = 17    # E Format- with explicit power of 10
SPSS_FMT_DATE           = 20    # Date format dd-mmm-yyyy
SPSS_FMT_TIME           = 21    # Time format hh:mm:ss.s
SPSS_FMT_DATETIME       = 22    # Date and Time
SPSS_FMT_ADATE          = 23    # Date format dd-mmm-yyyy
SPSS_FMT_JDATE          = 24    # Julian date - yyyyddd
SPSS_FMT_DTIME          = 25    # Date-time dd hh:mm:ss.s
SPSS_FMT_WKDAY          = 26    # Day of the week
SPSS_FMT_MONTH          = 27    # Month
SPSS_FMT_MOYR           = 28    # mmm yyyy
SPSS_FMT_QYR            = 29    # q Q yyyy
SPSS_FMT_WKYR           = 30    # ww WK yyyy
SPSS_FMT_PCT            = 31    # Percent - F followed by %
SPSS_FMT_DOT            = 32    # Like COMMA, switching dot for comma
SPSS_FMT_CCA            = 33    # User Programmable currency format
SPSS_FMT_CCB            = 34    # User Programmable currency format
SPSS_FMT_CCC            = 35    # User Programmable currency format
SPSS_FMT_CCD            = 36    # User Programmable currency format
SPSS_FMT_CCE            = 37    # User Programmable currency format
SPSS_FMT_EDATE          = 38    # Date in dd/mm/yyyy style
SPSS_FMT_SDATE          = 39    # Date in yyyy/mm/dd style
SPSS_FMT_MTIME          = 85    # Time format mm:ss.ss
SPSS_FMT_YMDHMS         = 86    # Date format yyyy-mm-dd hh:mm:ss.ss

# Return codes (OK)
SPSS_OK                         = 0
# Return codes (errors)
SPSS_FILE_OERROR                = 1
SPSS_FILE_WERROR                = 2
SPSS_FILE_RERROR                = 3
SPSS_FITAB_FULL                 = 4
SPSS_INVALID_HANDLE             = 5
SPSS_INVALID_FILE               = 6
SPSS_NO_MEMORY                  = 7
SPSS_OPEN_RDMODE                = 8
SPSS_OPEN_WRMODE                = 9
SPSS_INVALID_VARNAME            = 10
SPSS_DICT_EMPTY                 = 11
SPSS_VAR_NOTFOUND               = 12
SPSS_DUP_VAR                    = 13
SPSS_NUME_EXP                   = 14
SPSS_STR_EXP                    = 15
SPSS_SHORTSTR_EXP               = 16
SPSS_INVALID_VARTYPE            = 17
SPSS_INVALID_MISSFOR            = 18
SPSS_INVALID_COMPSW             = 19
SPSS_INVALID_PRFOR              = 20
SPSS_INVALID_WRFOR              = 21
SPSS_INVALID_DATE               = 22
SPSS_INVALID_TIME               = 23
SPSS_NO_VARIABLES               = 24
SPSS_MIXED_TYPES                = 25
SPSS_DUP_VALUE                  = 27
SPSS_INVALID_CASEWGT            = 28
SPSS_INCOMPATIBLE_DICT          = 29
SPSS_DICT_COMMIT                = 30
SPSS_DICT_NOTCOMMIT             = 31
SPSS_NO_TYPE2                   = 33
SPSS_NO_TYPE73                  = 41
SPSS_INVALID_DATEINFO           = 45
SPSS_NO_TYPE999                 = 46
SPSS_EXC_STRVALUE               = 47
SPSS_CANNOT_FREE                = 48
SPSS_BUFFER_SHORT               = 49
SPSS_INVALID_CASE               = 50
SPSS_INTERNAL_VLABS             = 51
SPSS_INCOMPAT_APPEND            = 52
SPSS_INTERNAL_D_A               = 53
SPSS_FILE_BADTEMP               = 54
SPSS_DEW_NOFIRST                = 55
SPSS_INVALID_MEASURELEVEL       = 56
SPSS_INVALID_7SUBTYPE           = 57
SPSS_INVALID_VARHANDLE          = 58
SPSS_INVALID_ENCODING           = 59
SPSS_FILES_OPEN                 = 60
SPSS_INVALID_MRSETDEF           = 70
SPSS_INVALID_MRSETNAME          = 71
SPSS_DUP_MRSETNAME              = 72
SPSS_BAD_EXTENSION              = 73
SPSS_INVALID_EXTENDEDSTRING     = 74
SPSS_INVALID_ATTRNAME           = 75
SPSS_INVALID_ATTRDEF            = 76
SPSS_INVALID_MRSETINDEX         = 77
SPSS_INVALID_VARSETDEF          = 78
SPSS_INVALID_ROLE               = 79
# Retern codes (warnings)
SPSS_EXC_LEN64                  = -1
SPSS_EXC_LEN120                 = -2
SPSS_EXC_VARLABEL               = -2
SPSS_EXC_LEN60                  = -4
SPSS_EXC_VALLABEL               = -4
SPSS_FILE_END                   = -5
SPSS_NO_VARSETS                 = -6
SPSS_EMPTY_VARSETS              = -7
SPSS_NO_LABELS                  = -8
SPSS_NO_LABEL                   = -9
SPSS_NO_CASEWGT                 = -10
SPSS_NO_DATEINFO                = -11
SPSS_NO_MULTRESP                = -12
SPSS_EMPTY_MULTRESP             = -13
SPSS_NO_DEW                     = -14
SPSS_EMPTY_DEW                  = -15

# measure levels
SPSS_MLVL_UNK       = 0
SPSS_MLVL_NOM       = 1
SPSS_MLVL_ORD       = 2
SPSS_MLVL_RAT       = 3

# alignments
SPSS_ALIGN_LEFT     = 0
SPSS_ALIGN_RIGHT    = 1
SPSS_ALIGN_CENTER   = 2

# roles
SPSS_ROLE_INPUT     = 0
SPSS_ROLE_TARGET    = 1
SPSS_ROLE_BOTH      = 2
SPSS_ROLE_NONE      = 3
SPSS_ROLE_PARTITION = 4
SPSS_ROLE_SPLIT     = 5
SPSS_ROLE_FREQUENCY = 6
SPSS_ROLE_RECORDID  = 7

# datetime constants for conversions
SPSS_ORIGIN_OFFSET = 12219379200
S_TO_NS = 1_000_000_000

# return codes
retcodes = {
    0: 'SPSS_OK',
    1: 'SPSS_FILE_OERROR',
    2: 'SPSS_FILE_WERROR',
    3: 'SPSS_FILE_RERROR',
    4: 'SPSS_FITAB_FULL',
    5: 'SPSS_INVALID_HANDLE',
    6: 'SPSS_INVALID_FILE',
    7: 'SPSS_NO_MEMORY',
    8: 'SPSS_OPEN_RDMODE',
    9: 'SPSS_OPEN_WRMODE',
    10: 'SPSS_INVALID_VARNAME',
    11: 'SPSS_DICT_EMPTY',
    12: 'SPSS_VAR_NOTFOUND',
    13: 'SPSS_DUP_VAR',
    14: 'SPSS_NUME_EXP',
    15: 'SPSS_STR_EXP',
    16: 'SPSS_SHORTSTR_EXP',
    17: 'SPSS_INVALID_VARTYPE',
    18: 'SPSS_INVALID_MISSFOR',
    19: 'SPSS_INVALID_COMPSW',
    20: 'SPSS_INVALID_PRFOR',
    21: 'SPSS_INVALID_WRFOR',
    22: 'SPSS_INVALID_DATE',
    23: 'SPSS_INVALID_TIME',
    24: 'SPSS_NO_VARIABLES',
    25: 'SPSS_MIXED_TYPES',
    27: 'SPSS_DUP_VALUE',
    28: 'SPSS_INVALID_CASEWGT',
    29: 'SPSS_INCOMPATIBLE_DICT',
    30: 'SPSS_DICT_COMMIT',
    31: 'SPSS_DICT_NOTCOMMIT',
    33: 'SPSS_NO_TYPE2',
    41: 'SPSS_NO_TYPE73',
    45: 'SPSS_INVALID_DATEINFO',
    46: 'SPSS_NO_TYPE999',
    47: 'SPSS_EXC_STRVALUE',
    48: 'SPSS_CANNOT_FREE',
    49: 'SPSS_BUFFER_SHORT',
    50: 'SPSS_INVALID_CASE',
    51: 'SPSS_INTERNAL_VLABS',
    52: 'SPSS_INCOMPAT_APPEND',
    53: 'SPSS_INTERNAL_D_A',
    54: 'SPSS_FILE_BADTEMP',
    55: 'SPSS_DEW_NOFIRST',
    56: 'SPSS_INVALID_MEASURELEVEL',
    57: 'SPSS_INVALID_7SUBTYPE',
    58: 'SPSS_INVALID_VARHANDLE',
    59: 'SPSS_INVALID_ENCODING',
    60: 'SPSS_FILES_OPEN',
    70: 'SPSS_INVALID_MRSETDEF',
    71: 'SPSS_INVALID_MRSETNAME',
    72: 'SPSS_DUP_MRSETNAME',
    73: 'SPSS_BAD_EXTENSION',
    74: 'SPSS_INVALID_EXTENDEDSTRING',
    75: 'SPSS_INVALID_ATTRNAME',
    76: 'SPSS_INVALID_ATTRDEF',
    77: 'SPSS_INVALID_MRSETINDEX',
    78: 'SPSS_INVALID_VARSETDEF',
    79: 'SPSS_INVALID_ROLE',
    -1: 'SPSS_EXC_LEN64',
    -2: 'SPSS_EXC_LEN120',
    -2: 'SPSS_EXC_VARLABEL',
    -4: 'SPSS_EXC_LEN60',
    -4: 'SPSS_EXC_VALLABEL',
    -5: 'SPSS_FILE_END',
    -6: 'SPSS_NO_VARSETS',
    -7: 'SPSS_EMPTY_VARSETS',
    -8: 'SPSS_NO_LABELS',
    -9: 'SPSS_NO_LABEL',
    -10: 'SPSS_NO_CASEWGT',
    -11: 'SPSS_NO_DATEINFO',
    -12: 'SPSS_NO_MULTRESP',
    -13: 'SPSS_EMPTY_MULTRESP',
    -14: 'SPSS_NO_DEW',
    -15: 'SPSS_EMPTY_DEW'
    }

spss_formats = {
    1: 'SPSS_FMT_A',            # Alphanumeric
    2: 'SPSS_FMT_AHEX',         # Alphanumeric hexadecimal
    3: 'SPSS_FMT_COMMA',        # F Format with commas
    4: 'SPSS_FMT_DOLLAR',       # Commas and floating dollar sign
    5: 'SPSS_FMT_F',            # Default Numeric Format
    6: 'SPSS_FMT_IB',           # Integer binary
    7: 'SPSS_FMT_PIBHEX',       # Positive integer binary - hex
    8: 'SPSS_FMT_P',            # Packed decimal
    9: 'SPSS_FMT_PIB',          # Positive integer binary unsigned
    10: 'SPSS_FMT_PK',          # Positive integer binary unsigned
    11: 'SPSS_FMT_RB',          # Floating point binary
    12: 'SPSS_FMT_RBHEX',       # Floating point binary hex
    15: 'SPSS_FMT_Z',           # Zoned decimal
    16: 'SPSS_FMT_N',           # N Format- unsigned with leading 0s
    17: 'SPSS_FMT_E',           # E Format- with explicit power of 10
    20: 'SPSS_FMT_DATE',        # Date format dd-mmm-yyyy
    21: 'SPSS_FMT_TIME',        # Time format hh:mm:ss.s
    22: 'SPSS_FMT_DATETIME',    # Date and Time
    23: 'SPSS_FMT_ADATE',       # Date format dd-mmm-yyyy
    24: 'SPSS_FMT_JDATE',       # Julian date - yyyyddd
    25: 'SPSS_FMT_DTIME',       # Date-time dd hh:mm:ss.s
    26: 'SPSS_FMT_WKDAY',       # Day of the week
    27: 'SPSS_FMT_MONTH',       # Month
    28: 'SPSS_FMT_MOYR',        # mmm yyyy
    29: 'SPSS_FMT_QYR',         # q Q yyyy
    30: 'SPSS_FMT_WKYR',        # ww WK yyyy
    31: 'SPSS_FMT_PCT',         # Percent - F followed by %
    32: 'SPSS_FMT_DOT',         # Like COMMA, switching dot for comma
    33: 'SPSS_FMT_CCA',         # User Programmable currency format
    34: 'SPSS_FMT_CCB',         # User Programmable currency format
    35: 'SPSS_FMT_CCC',         # User Programmable currency format
    36: 'SPSS_FMT_CCD',         # User Programmable currency format
    37: 'SPSS_FMT_CCE',         # User Programmable currency format
    38: 'SPSS_FMT_EDATE',       # Date in dd/mm/yyyy style
    39: 'SPSS_FMT_SDATE',       # Date in yyyy/mm/dd style
    85: 'SPSS_FMT_MTIME',       # Time format mm:ss.ss
    86: 'SPSS_FMT_YMDHMS'       # Date format yyyy-mm-dd hh:mm:ss.ss
    }

spss_formats_rev = {v:k for k,v in spss_formats.items()}
spss_formats_simple = {k:v.split('_', 2)[-1] for k,v in spss_formats.items()}
spss_formats_simple_rev = {v:k for k,v in spss_formats_simple.items()}

spss_string_formats = [SPSS_FMT_A, SPSS_FMT_AHEX]

spss_date_formats = [
    SPSS_FMT_DATE,
    SPSS_FMT_ADATE,
    SPSS_FMT_JDATE,
    SPSS_FMT_WKDAY,
    SPSS_FMT_MONTH,
    SPSS_FMT_MOYR,
    SPSS_FMT_QYR,
    SPSS_FMT_WKYR,
    SPSS_FMT_EDATE,
    SPSS_FMT_SDATE
    ]

spss_time_formats = [
    SPSS_FMT_TIME,
    SPSS_FMT_MTIME
    ]

spss_datetime_formats = [
    SPSS_FMT_DTIME,
    SPSS_FMT_DATETIME,
    SPSS_FMT_YMDHMS
    ]

max_lengths = {
    'SPSS_MAX_VARNAME':            64,     # Variable name
    'SPSS_MAX_SHORTVARNAME':        8,     # Short (compatibility) variable name
    'SPSS_MAX_SHORTSTRING':         8,     # Short string variable
    'SPSS_MAX_IDSTRING':           64,     # File label string
    'SPSS_MAX_LONGSTRING':      32767,     # Long string variable
    'SPSS_MAX_VALLABEL':          120,     # Value label
    'SPSS_MAX_VARLABEL':          256,     # Variable label
    'SPSS_MAX_ENCODING':           64,     # Maximum encoding text
    'SPSS_MAX_7SUBTYPE':           40,     # Maximum record 7 subtype
    'SPSS_MAX_PASSWORD':           10      # Maximum password
    }

missing_value_types = {
    'SPSS_NO_MISSVAL':            0,
    'SPSS_ONE_MISSVAL':           1,
    'SPSS_TWO_MISSVAL':           2,
    'SPSS_THREE_MISSVAL':         3,
    'SPSS_MISS_RANGE':           -2,
    'SPSS_MISS_RANGEANDVAL':     -3
    }

missing_value_types_rev = {v:k for k,v in missing_value_types.items()}

measure_levels = {
    'unknown': 0,
    'nominal': 1,
    'ordinal': 2,
    'scale': 3
    }

measure_levels_str = {v:k for k,v in measure_levels.items()}

alignments = {
    'left': 0,
    'right': 1,
    'center': 2
    }

alignments_str = {v:k for k,v in alignments.items()}

roles = {
    'input': 0,
    'target': 1,
    'both': 2,
    'none': 3,
    'partition': 4,
    'split': 5,
    'frequency': 6,
    'recordid': 7
    }

roles_str = {v:k for k,v in roles.items()}
