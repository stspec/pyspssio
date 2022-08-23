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

# datetime constants for conversions
SPSS_ORIGIN_OFFSET = 12219379200
S_TO_NS = 10 ** 9

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

spss_string_formats = [1,2]

spss_date_formats = [20,23,24,25,26,27,28,29,30,38,39]
spss_time_formats = [21,85]
spss_datetime_formats = [22,86]

spss_datetime_formats_to_convert = spss_date_formats + spss_time_formats + spss_datetime_formats

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

measure_levels = {'unknown': 0,
                  'nominal': 1,
                  'ordinal': 2,
                  'scale': 3}

measure_levels_str = {v:k for k,v in measure_levels.items()}

alignments = {'left': 0, 'right': 1, 'center': 2}

alignments_str = {v:k for k,v in alignments.items()}

roles = {'input': 0,
         'target': 1,
         'both': 2,
         'none': 3,
         'partition': 4,
         'split': 5,
         'frequency': 6,
         'recordid': 7}

roles_str = {v:k for k,v in roles.items()}
