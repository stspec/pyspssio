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

import re

from ctypes import *

from .errors import warn_or_raise
from .constants import *
from .constants_map import *
from .spssfile import SPSSFile


def varformat_to_tuple(varformat):
    """Convert variable format as string to tuple of integers"""

    if isinstance(varformat, (tuple, list)):
        return varformat

    f_split = re.split(r"([^\d]+)|[\.]", varformat + ".0")

    f_type = spss_formats_simple_rev[f_split[1]]
    f_width = int(f_split[2])
    f_dec = int(f_split[4])

    return (f_type, f_width, f_dec)


class Header(SPSSFile):
    """Class for getting and setting metadata"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def file_attributes(self):
        """Get or set file attributes"""

        func = self.spssio.spssGetFileAttributes

        def func_config(array_size=0):
            argtypes = [
                c_int,
                POINTER(POINTER(c_char_p * array_size)),
                POINTER(POINTER(c_char_p * array_size)),
                POINTER(c_int),
            ]
            attr_names = POINTER(c_char_p * array_size)()
            attr_text = POINTER(c_char_p * array_size)()
            num_attributes = c_int()
            return argtypes, attr_names, attr_text, num_attributes

        # first get initial size
        argtypes, attr_names, attr_text, num_attributes = func_config()
        func.argtypes = argtypes
        retcode = func(self.fh, attr_names, attr_text, num_attributes)
        warn_or_raise(retcode, func)

        # get actual array size and clean
        array_size = num_attributes.value
        self.spssio.spssFreeAttributes(attr_names, attr_text, num_attributes)

        if array_size == 0:
            return {}

        else:
            # get attributes
            argtypes, attr_names, attr_text, num_attributes = func_config(array_size)
            func.argtypes = argtypes
            retcode = func(self.fh, attr_names, attr_text, num_attributes)
            warn_or_raise(retcode, func)

            # clean
            self.spssio.spssFreeAttributes(attr_names, attr_text, num_attributes)

            attr_names = (x.decode(self.encoding) for x in attr_names[0])
            attr_text = (x.decode(self.encoding) for x in attr_text[0])

            return dict(zip(attr_names, attr_text))

    @file_attributes.setter
    def file_attributes(self, attributes):
        array_size = len(attributes)
        attr_names = []
        attr_text = []

        for name, text in attributes.items():
            attr_names.append(str(name).encode(self.encoding))
            attr_text.append(str(text).encode(self.encoding))

        attr_names = (c_char_p * array_size)(*attr_names)
        attr_text = (c_char_p * array_size)(*attr_text)

        func = self.spssio.spssSetFileAttributes
        func.argtypes = [
            c_int,
            POINTER(c_char_p * array_size),
            POINTER(c_char_p * array_size),
            c_int,
        ]

        retcode = func(self.fh, attr_names, attr_text, array_size)
        warn_or_raise(retcode, func)

    @property
    def var_names(self):
        """List of variable names"""

        num_vars = self.var_count

        func = self.spssio.spssGetVarNames
        func.argtypes = [
            c_int,
            POINTER(c_int),
            POINTER(POINTER(c_char_p * num_vars)),
            POINTER(POINTER(c_int * num_vars)),
        ]

        _num_vars = c_int()
        var_names = POINTER(c_char_p * num_vars)()
        var_types = POINTER(c_int * num_vars)()

        retcode = func(self.fh, _num_vars, var_names, var_types)
        warn_or_raise(retcode, func)
        var_name_list = [var_names[0][i].decode(self.encoding) for i in range(num_vars)]
        self.spssio.spssFreeVarNames(var_names, var_types, _num_vars)
        return var_name_list

    @property
    def var_types(self):
        """Get or set variable names and their types"""

        num_vars = self.var_count

        func = self.spssio.spssGetVarNames
        func.argtypes = [
            c_int,
            POINTER(c_int),
            POINTER(POINTER(c_char_p * num_vars)),
            POINTER(POINTER(c_int * num_vars)),
        ]

        _num_vars = c_int()
        var_names = POINTER(c_char_p * num_vars)()
        var_types = POINTER(c_int * num_vars)()

        retcode = func(self.fh, _num_vars, var_names, var_types)
        warn_or_raise(retcode, func)
        var_types_dict = {
            var_names[0][i].decode(self.encoding): var_types[0][i] for i in range(num_vars)
        }
        self.spssio.spssFreeVarNames(var_names, var_types, _num_vars)
        return var_types_dict

    @var_types.setter
    def var_types(self, var_types):
        for var_name, var_type in var_types.items():
            self._add_var(var_name, var_type)

    def _add_var(self, var_name, var_type=0):
        func = self.spssio.spssSetVarName
        func.argtypes = [c_int, c_char_p, c_int]
        retcode = func(self.fh, var_name.encode(self.encoding), c_int(var_type))
        warn_or_raise(retcode, func, var_name, var_type)

    def _get_var_handle(self, var_name):
        func = self.spssio.spssGetVarHandle
        func.argtypes = [c_int, c_char_p, POINTER(c_double)]

        var_handle = c_double()
        retcode = func(self.fh, var_name.encode(self.encoding), var_handle)
        warn_or_raise(retcode, func, var_name)
        return var_handle

    @property
    def var_handles(self):
        """Get variable handles"""

        func = self.spssio.spssGetVarHandle
        func.argtypes = [c_int, c_char_p, POINTER(c_double)]

        var_handles = {}
        for var_name in self.var_names:
            var_handle = c_double()
            retcode = func(self.fh, var_name.encode(self.encoding), var_handle)
            warn_or_raise(retcode, func, var_name)
            var_handles[var_name] = var_handle

        return var_handles

    def _get_var_format(self, var_name):
        func = self.spssio.spssGetVarPrintFormat
        func.argtypes = [c_int, c_char_p, POINTER(c_int), POINTER(c_int), POINTER(c_int)]

        f_type = c_int()
        f_dec = c_int()
        f_width = c_int()
        retcode = func(self.fh, var_name.encode(self.encoding), f_type, f_dec, f_width)
        warn_or_raise(retcode, func, var_name)
        return (f_type.value, f_width.value, f_dec.value)

    @property
    def var_formats_tuple(self):
        """Get variable formats in tuple style (Type, Width, Decimals)

        ex. (5, 8, 2) instead of F8.2
        """

        var_formats = {}
        for var_name in self.var_names:
            var_formats[var_name] = self._get_var_format(var_name)
        return var_formats

    @property
    def var_formats(self):
        """Get or set variable formats

        Parameters
        ----------
        var_formats : dict
            Dictionary of variable names and formats (normal or tuple)

        Returns
        -------
        dict
            Dictionary of variable names and formats (normal)

        Use var_formats_tuple property to get formats in tuple style
        """

        var_formats = {}
        for var_name in self.var_names:
            f_type, f_width, f_dec = self._get_var_format(var_name)
            var_formats[var_name] = (
                spss_formats_simple[f_type]
                + str(int(f_width))
                + ("." + str(int(f_dec)) if f_dec else "")
            )
        return var_formats

    @var_formats.setter
    def var_formats(self, var_formats):
        var_names = self.var_names

        for var_name, var_format in var_formats.items():
            if var_name in var_names:

                # convert to tuple in case string type is supplied
                var_format = varformat_to_tuple(var_format)

                f_type, f_width, f_dec = var_format

                for func in (self.spssio.spssSetVarPrintFormat, self.spssio.spssSetVarWriteFormat):
                    func.argtypes = [c_int, c_char_p, c_int, c_int, c_int]

                    retcode = func(
                        self.fh,
                        var_name.encode(self.encoding),
                        c_int(f_type),
                        c_int(f_dec),
                        c_int(f_width),
                    )

                    warn_or_raise(retcode, func, var_name, var_format)

    @property
    def var_measure_levels(self):
        """Get or set variable measure levels

        0 = Unknown
        1 = Nominal
        2 = Ordinal
        3 = Scale
        """

        func = self.spssio.spssGetVarMeasureLevel
        func.argtypes = [c_int, c_char_p, POINTER(c_int)]

        var_levels = {}
        for var_name in self.var_names:
            level = c_int()
            retcode = func(self.fh, var_name.encode(self.encoding), level)
            warn_or_raise(retcode, func, var_name)
            var_levels[var_name] = measure_levels_str[level.value]
        return var_levels

    @var_measure_levels.setter
    def var_measure_levels(self, var_measure_levels):
        var_names = self.var_names

        func = self.spssio.spssSetVarMeasureLevel
        func.argtypes = [c_int, c_char_p, c_int]

        for var_name, measure_level in var_measure_levels.items():
            measure_level = measure_levels.get(str(measure_level).lower(), measure_level)
            if var_name in var_names:
                retcode = func(self.fh, var_name.encode(self.encoding), c_int(measure_level))
                warn_or_raise(retcode, func, var_name, measure_level)

    @property
    def var_alignments(self):
        """Get or set variable alignments

        0 = SPSS_ALIGN_LEFT
        1 = SPSS_ALIGN_RIGHT
        2 = SPSS_ALIGN_CENTER
        """

        func = self.spssio.spssGetVarAlignment
        func.argtypes = [c_int, c_char_p, POINTER(c_int)]

        var_alignments = {}
        for var_name in self.var_names:
            align = c_int()
            retcode = func(self.fh, var_name.encode(self.encoding), align)
            warn_or_raise(retcode, func, var_name)
            var_alignments[var_name] = alignments_str[align.value]
        return var_alignments

    @var_alignments.setter
    def var_alignments(self, var_alignments):
        var_names = self.var_names

        func = self.spssio.spssSetVarAlignment
        func.argtypes = [c_int, c_char_p, c_int]

        for var_name, align in var_alignments.items():
            align = alignments.get(str(align).lower(), align)
            if var_name in var_names:
                retcode = func(self.fh, var_name.encode(self.encoding), align)
                warn_or_raise(retcode, func, var_name, align)

    @property
    def var_column_widths(self):
        """Get or set column widths

        0 = Auto
        """

        func = self.spssio.spssGetVarColumnWidth
        func.argtypes = [c_int, c_char_p, POINTER(c_int)]

        widths = {}
        for var_name in self.var_names:
            column_width = c_int()
            retcode = func(self.fh, var_name.encode(self.encoding), column_width)
            warn_or_raise(retcode, func, var_name)
            widths[var_name] = column_width.value
        return widths

    @var_column_widths.setter
    def var_column_widths(self, var_column_widths):
        var_names = self.var_names

        func = self.spssio.spssSetVarColumnWidth
        func.argtypes = [c_int, c_char_p, c_int]

        for var_name, column_width in var_column_widths.items():
            if var_name in var_names:
                retcode = func(self.fh, var_name.encode(self.encoding), column_width)
                warn_or_raise(retcode, func, var_name, column_width)

    @property
    def var_labels(self):
        """Get or set variable labels"""

        len_buff = SPSS_MAX_VARLABEL + 1
        buffer = create_string_buffer(len_buff)

        func = self.spssio.spssGetVarLabelLong
        func.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_int)]

        var_labels = {}
        for var_name in self.var_names:
            len_label = c_int()
            retcode = func(self.fh, var_name.encode(self.encoding), buffer, len_buff, len_label)
            warn_or_raise(retcode, func, var_name)
            var_labels[var_name] = buffer.value.decode(self.encoding)
        return var_labels

    @var_labels.setter
    def var_labels(self, labels):
        var_names = self.var_names

        func = self.spssio.spssSetVarLabel
        func.argtypes = [c_int, c_char_p, c_char_p]

        for var_name, var_label in labels.items():
            if var_name in var_names:

                retcode = func(
                    self.fh, var_name.encode(self.encoding), var_label.encode(self.encoding)
                )

                warn_or_raise(retcode, func, var_name, var_label)

    @property
    def var_roles(self):
        """Get or set variable roles

        0 = SPSS_ROLE_INPUT
        1 = SPSS_ROLE_TARGET
        2 = SPSS_ROLE_BOTH
        3 = SPSS_ROLE_NONE
        4 = SPSS_ROLE_PARTITION
        5 = SPSS_ROLE_SPLIT
        6 = SPSS_ROLE_FREQUENCY
        7 = SPSS_ROLE_RECORDID
        """

        func = self.spssio.spssGetVarRole
        func.argtypes = [c_int, c_char_p, POINTER(c_int)]

        var_roles = {}
        for var_name in self.var_names:
            role = c_int()
            retcode = func(self.fh, var_name.encode(self.encoding), role)
            warn_or_raise(retcode, func, var_name)
            var_roles[var_name] = roles_str[role.value]

        return var_roles

    @var_roles.setter
    def var_roles(self, var_roles):
        var_names = self.var_names
        func = self.spssio.spssSetVarRole
        func.argtypes = [c_int, c_char_p, c_int]

        for var_name, role in var_roles.items():
            role = roles.get(str(role).lower(), role)
            if var_name in var_names:
                retcode = func(self.fh, var_name.encode(self.encoding), role)
                warn_or_raise(retcode, func, var_name, role)

    def _get_var_n_value_labels(self, var_name):
        func = self.spssio.spssGetVarNValueLabels

        def func_config(var_name, size=0):
            argtypes = [
                c_int,
                c_char_p,
                POINTER(POINTER(c_double * size)),
                POINTER(POINTER(c_char_p * size)),
                POINTER(c_int),
            ]

            values_arr = POINTER((c_double * size))()
            labels_arr = POINTER((c_char_p * size))()
            num_labels = c_int()
            return argtypes, var_name, values_arr, labels_arr, num_labels

        # initial function call to get number of labels
        argtypes, var_name, values_arr, labels_arr, num_labels = func_config(var_name)
        func.argtypes = argtypes
        retcode = func(self.fh, var_name.encode(self.encoding), values_arr, labels_arr, num_labels)
        if retcode > 0:
            self.spssio.spssFreeVarNValueLabels(values_arr, labels_arr, num_labels)
            warn_or_raise(retcode, func, var_name)
        elif num_labels.value > 0:
            # if function call was successful and variable has value labels
            argtypes, var_name, values_arr, labels_arr, num_labels = func_config(
                var_name, num_labels.value
            )
            func.argtypes = argtypes
            retcode = func(
                self.fh, var_name.encode(self.encoding), values_arr, labels_arr, num_labels
            )
            warn_or_raise(retcode, func, var_name)
            value_labels = {
                values_arr[0][i]: labels_arr[0][i].decode(self.encoding)
                for i in range(num_labels.value)
            }
            self.spssio.spssFreeVarNValueLabels(values_arr, labels_arr, num_labels)
            return value_labels
        else:
            return {}

    def _get_var_c_value_labels(self, var_name):
        func = self.spssio.spssGetVarCValueLabels

        def func_config(var_name, size=0):
            argtypes = [
                c_int,
                c_char_p,
                POINTER(POINTER(c_char_p * size)),
                POINTER(POINTER(c_char_p * size)),
                POINTER(c_int),
            ]

            values_arr = POINTER((c_char_p * size))()
            labels_arr = POINTER((c_char_p * size))()
            num_labels = c_int()
            return argtypes, var_name, values_arr, labels_arr, num_labels

        # initial function call to get number of labels
        argtypes, var_name, values_arr, labels_arr, num_labels = func_config(var_name)
        func.argtypes = argtypes
        retcode = func(self.fh, var_name.encode(self.encoding), values_arr, labels_arr, num_labels)
        if retcode > 0:
            self.spssio.spssFreeVarCValueLabels(values_arr, labels_arr, num_labels)
            warn_or_raise(retcode, func, var_name)
        elif num_labels.value > 0:
            # if function call was successful and variable has value labels
            argtypes, var_name, values_arr, labels_arr, num_labels = func_config(
                var_name, num_labels.value
            )
            func.argtypes = argtypes
            retcode = func(
                self.fh, var_name.encode(self.encoding), values_arr, labels_arr, num_labels
            )
            warn_or_raise(retcode, func, var_name)
            value_labels = {
                values_arr[0][i]
                .decode(self.encoding)
                .rstrip(): labels_arr[0][i]
                .decode(self.encoding)
                for i in range(num_labels.value)
            }
            self.spssio.spssFreeVarCValueLabels(values_arr, labels_arr, num_labels)
            return value_labels
        else:
            return {}

    @property
    def var_value_labels(self):
        """Get or set value labels

        Note: numeric variables or string variables w/ length <= 8 only
        """

        var_value_labels = {}
        for var_name, var_type in self.var_types.items():
            if var_type == 0:
                var_value_labels[var_name] = self._get_var_n_value_labels(var_name)
            elif var_type <= 8:
                var_value_labels[var_name] = self._get_var_c_value_labels(var_name)
        return {k: v for k, v in var_value_labels.items() if v}

    def _set_var_n_value_label(self, var_name, value, label):
        func = self.spssio.spssSetVarNValueLabel
        func.argtypes = [c_int, c_char_p, c_double, c_char_p]
        retcode = func(
            self.fh, var_name.encode(self.encoding), c_double(value), label.encode(self.encoding)
        )
        warn_or_raise(retcode, func, var_name, value, label)

    def _set_var_c_value_label(self, var_name, value, label):
        func = self.spssio.spssSetVarCValueLabel
        func.argtypes = [c_int, c_char_p, c_char_p, c_char_p]
        retcode = func(
            self.fh,
            var_name.encode(self.encoding),
            value.encode(self.encoding),
            label.encode(self.encoding),
        )
        warn_or_raise(retcode, func, var_name, value, label)

    @var_value_labels.setter
    def var_value_labels(self, var_value_labels):
        var_types = self.var_types
        for var_name, value_labels in var_value_labels.items():
            var_type = var_types.get(var_name)
            if var_type is not None:
                if var_type:
                    func = self._set_var_c_value_label
                else:
                    func = self._set_var_n_value_label
                for value, label in value_labels.items():
                    func(var_name, value, label)

    @property
    def mrsets(self):
        """Get or set multi response set definitions"""

        mrsets_dict = {}

        func = self.spssio.spssGetMultRespDefs
        func.argtypes = [c_int, POINTER(c_char_p)]
        mrsets_string = c_char_p()
        retcode = func(self.fh, mrsets_string)
        if retcode > 0:
            self.spssio.spssFreeMultRespDefs(mrsets_string)
            warn_or_raise(retcode, func)
        elif mrsets_string:
            mrsets = mrsets_string.value.decode(self.encoding)  # pylint: disable=no-member
            mrsets = mrsets.strip().split("\n")
            mrsets = [x.split("=", 2) for x in mrsets]
            for mrset in mrsets:
                d = {}
                setname, attr = mrset
                if attr[0].upper() == "D":
                    d["type"] = "D"
                    idx = 1
                    d["value_length"] = attr[idx:].split(" ", 1)[0]
                    idx += len(d["value_length"]) + 1
                    d["counted_value"] = attr[idx:][: int(d["value_length"].strip())]
                    idx += len(d["counted_value"]) + 1
                    d["label_length"] = attr[idx:].split(" ", 1)[0]
                    idx += len(d["label_length"]) + 1
                    d["label"] = attr[idx:][: int(d["label_length"].strip())]
                    idx += len(d["label"]) + 1
                    d["variable_list"] = attr[idx:].split()
                    mrsets_dict[setname] = d
                elif attr[0].upper() == "C":
                    d["type"] = "C"
                    idx = 2
                    d["value_length"], d["counted_value"] = None, None
                    d["label_length"] = attr[idx:].split(" ", 1)[0]
                    idx += len(d["label_length"]) + 1
                    d["label"] = attr[idx:][: int(d["label_length"].strip())]
                    idx += len(d["label"]) + 1
                    d["variable_list"] = attr[idx:].split()
                    mrsets_dict[setname] = d

        # clean
        self.spssio.spssFreeMultRespDefs(mrsets_string)
        warn_or_raise(retcode, func)

        if len(mrsets_dict):
            var_types = self.var_types
            for mrset, d in mrsets_dict.items():
                d["label_length"] = int(d["label_length"])
                if d["value_length"] is not None:
                    d["value_length"] = int(d["value_length"])
                if d["counted_value"] is not None and var_types[d["variable_list"][0]] == 0:
                    d["counted_value"] = int(d["counted_value"])

        return mrsets_dict

    @mrsets.setter
    def mrsets(self, mrsets):
        """Get or set multiple response set definitions

        Returns
        -------
        dict
            set_name
                - type : str ('C' or 'D')
                - counted_value : int or str (for 'D' type only)
                - label : str
                - variable_list : list of variables included in set
        """

        var_types = self.var_types

        # prepare mrsets
        mrset_list = []
        for mrset, d in mrsets.items():
            if mrset[0] != "$":
                mrset = "$" + mrset
            label = str(d.get("label", mrset[1:]))
            label_length = str(len(label.encode(self.encoding)))
            set_type = d.get("type")

            variable_list = [var for var in d.get("variable_list", []) if var in var_types]
            if len(variable_list):
                # only attempt to add if at least one variable is present
                if not isinstance(variable_list, (list, tuple)):
                    raise TypeError(f"Expected 'list' or 'tuple' for variable list - {mrset}")
                if set_type is None:
                    raise ValueError(
                        f"Missing mrset 'type' for {mrset}: must be C (category) or D (dichotomous)"
                    )
                elif set_type.upper() == "C":
                    mrset_list.append(
                        " ".join(
                            [mrset + "=" + set_type, label_length, label, " ".join(variable_list)]
                        )
                    )
                elif set_type.upper() == "D":
                    counted_value = d.get("counted_value")
                    if counted_value is None:
                        raise ValueError(f"Missing mrset 'counted_value' for {mrset}")
                    else:
                        if var_types[variable_list[0]] == 0:
                            counted_value = int(float(counted_value))
                        counted_value = str(counted_value)
                        value_length = str(len(counted_value))
                    mrset_list.append(
                        " ".join(
                            [
                                mrset + "=" + set_type + value_length,
                                counted_value,
                                label_length,
                                label,
                                " ".join(variable_list),
                            ]
                        )
                    )
        mrsets = "\n".join(mrset_list).encode(self.encoding)

        # set mrsets
        func = self.spssio.spssSetMultRespDefs
        func.argtypes = [c_int, c_char_p]
        retcode = func(self.fh, mrsets)
        warn_or_raise(retcode, func)

    @property
    def case_size(self):
        """Case size in bytes"""

        func = self.spssio.spssGetCaseSize
        func.argtypes = [c_int, POINTER(c_long)]
        case_size = c_long()
        retcode = func(self.fh, case_size)
        warn_or_raise(retcode, func)
        return case_size.value

    @property
    def case_weight_var(self):
        """Get or set case weight variable"""

        func = self.spssio.spssGetCaseWeightVar
        case_weight_var = create_string_buffer(SPSS_MAX_VARNAME + 1)
        retcode = func(self.fh, case_weight_var)
        warn_or_raise(retcode, func)
        return case_weight_var.value.decode(self.encoding)

    @case_weight_var.setter
    def case_weight_var(self, var_name):
        func = self.spssio.spssSetCaseWeightVar
        func.argtypes = [c_int, c_char_p]
        retcode = func(self.fh, var_name.encode(self.encoding))
        warn_or_raise(retcode, func, var_name)

    def _get_var_n_missing_values(self, var_name):
        func = self.spssio.spssGetVarNMissingValues
        func.argtypes = [
            c_int,
            c_char_p,
            POINTER(c_int),
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
        ]

        missing_format = c_int()
        val_1, val_2, val_3 = c_double(), c_double(), c_double()
        retcode = func(
            self.fh, var_name.encode(self.encoding), missing_format, val_1, val_2, val_3
        )
        warn_or_raise(retcode, func, var_name)

        missing_format = missing_format.value
        missing_values = [val_1.value, val_2.value, val_3.value]

        return (missing_format, missing_values)

    def _get_var_c_missing_values(self, var_name, var_type):
        """Will not return missing values if variable type > 8 (ex. A25)"""

        func = self.spssio.spssGetVarCMissingValues
        func.argtypes = [c_int, c_char_p, POINTER(c_int), c_char_p, c_char_p, c_char_p]

        missing_format = c_int()
        val_1 = create_string_buffer(var_type + 1)
        val_2 = create_string_buffer(var_type + 1)
        val_3 = create_string_buffer(var_type + 1)

        retcode = func(
            self.fh, var_name.encode(self.encoding), missing_format, val_1, val_2, val_3
        )
        warn_or_raise(retcode, func, var_name)

        missing_format = missing_format.value
        missing_values = [
            val_1.value.decode(self.encoding).rstrip(),
            val_2.value.decode(self.encoding).rstrip(),
            val_3.value.decode(self.encoding).rstrip(),
        ]

        return (missing_format, missing_values)

    @property
    def var_missing_values(self):
        """Get or set missing values

        For missing ranges, the following keywords can be used inplace of numeric values:
            - low: -inf, lo, low, lowest
            - high: inf, hi, high, highest
        """

        var_missing_values = {}
        for var_name, var_type in self.var_types.items():

            if var_type:
                missing_format, missing_values = self._get_var_c_missing_values(var_name, var_type)
            else:
                missing_format, missing_values = self._get_var_n_missing_values(var_name)

            if missing_format == SPSS_NO_MISSVAL:
                var_missing_values[var_name] = None
            elif missing_format in [SPSS_ONE_MISSVAL, SPSS_TWO_MISSVAL, SPSS_THREE_MISSVAL]:
                var_missing_values[var_name] = {"values": missing_values[:missing_format]}
            elif missing_format in [SPSS_MISS_RANGE, SPSS_MISS_RANGEANDVAL]:
                low, high = missing_values[:2]
                low = float("-inf") if low <= self.low_value else low
                high = float("inf") if high >= self.high_value else high
                var_missing_values[var_name] = {"lo": low, "hi": high}
                if missing_format == SPSS_MISS_RANGEANDVAL:
                    var_missing_values[var_name]["values"] = missing_values[2:3]

        return {k: v for k, v in var_missing_values.items() if v}

    @var_missing_values.setter
    def var_missing_values(self, var_missing_values):
        var_types = self.var_types

        for var_name, missing_values in var_missing_values.items():
            var_type = var_types.get(var_name)

            if var_type:
                func = self.spssio.spssSetVarCMissingValues
                func.argtypes = [c_int, c_char_p, c_int, c_char_p, c_char_p, c_char_p]
                discrete_values = missing_values.get("values", [])
                missing_format = min(3, len(discrete_values))
                val_1 = "" if missing_format < SPSS_ONE_MISSVAL else discrete_values[0]
                val_2 = "" if missing_format < SPSS_TWO_MISSVAL else discrete_values[1]
                val_3 = "" if missing_format < SPSS_THREE_MISSVAL else discrete_values[2]

                retcode = func(
                    self.fh,
                    var_name.encode(self.encoding),
                    c_int(missing_format),
                    val_1.encode(self.encoding),
                    val_2.encode(self.encoding),
                    val_3.encode(self.encoding),
                )

                warn_or_raise(retcode, func, var_name)

            elif var_type == 0:
                func = self.spssio.spssSetVarNMissingValues
                func.argtypes = [c_int, c_char_p, c_int, c_double, c_double, c_double]

                low = missing_values.get("lo")
                high = missing_values.get("hi")

                discrete_values = missing_values.get("values", [])

                if low is not None and high is not None:

                    if str(low) in ["-inf", "lo", "low", "lowest"] or low <= self.low_value:
                        low = self.low_value

                    if str(high) in ["inf", "hi", "high", "highest"] or high >= self.high_value:
                        high = self.high_value

                    val_1 = low
                    val_2 = high

                    if len(discrete_values):
                        missing_format = SPSS_MISS_RANGEANDVAL
                        val_3 = discrete_values[0]
                    else:
                        missing_format = SPSS_MISS_RANGE
                        val_3 = self.sysmis
                else:
                    missing_format = min(3, len(discrete_values))
                    val_1 = (
                        self.sysmis if missing_format < SPSS_ONE_MISSVAL else discrete_values[0]
                    )
                    val_2 = (
                        self.sysmis if missing_format < SPSS_TWO_MISSVAL else discrete_values[1]
                    )
                    val_3 = (
                        self.sysmis if missing_format < SPSS_THREE_MISSVAL else discrete_values[2]
                    )

                retcode = func(
                    self.fh,
                    var_name.encode(self.encoding),
                    c_int(missing_format),
                    c_double(val_1),
                    c_double(val_2),
                    c_double(val_3),
                )

                warn_or_raise(retcode, func, var_name)

    def _get_var_attributes(self, var_name):
        """Get attributes for a single variable"""

        func = self.spssio.spssGetVarAttributes
        clean = self.spssio.spssFreeAttributes

        def func_config(array_size=0):
            argtypes = [
                c_int,
                c_char_p,
                POINTER(POINTER(c_char_p * array_size)),
                POINTER(POINTER(c_char_p * array_size)),
                POINTER(c_int),
            ]
            attr_names = POINTER(c_char_p * array_size)()
            attr_text = POINTER(c_char_p * array_size)()
            num_attributes = c_int()
            return argtypes, attr_names, attr_text, num_attributes

        # first get initial size
        argtypes, attr_names, attr_text, num_attributes = func_config()
        func.argtypes = argtypes
        retcode = func(
            self.fh, var_name.encode(self.encoding), attr_names, attr_text, num_attributes
        )
        warn_or_raise(retcode, func)

        # get actual array size and clean
        array_size = num_attributes.value
        retcode = clean(attr_names, attr_text, num_attributes)
        warn_or_raise(retcode, clean)

        if array_size == 0:
            return {}

        else:
            # get attributes
            argtypes, attr_names, attr_text, num_attributes = func_config(array_size)
            func.argtypes = argtypes
            retcode = func(
                self.fh, var_name.encode(self.encoding), attr_names, attr_text, num_attributes
            )
            warn_or_raise(retcode, func)

            # clean
            retcode = clean(attr_names, attr_text, num_attributes)
            warn_or_raise(retcode, clean)

            attr_names = (x.decode(self.encoding) for x in attr_names[0])
            attr_text = (x.decode(self.encoding) for x in attr_text[0])

            return dict(zip(attr_names, attr_text))

    @property
    def var_attributes(self):
        """Get and set arbitrary variable properties"""

        var_attributes = {}
        for var_name in self.var_names:
            attributes = self._get_var_attributes(var_name)
            if attributes:
                var_attributes[var_name] = attributes

        return var_attributes

    @var_attributes.setter
    def var_attributes(self, var_attributes):

        func = self.spssio.spssSetVarAttributes

        for var_name, attributes in var_attributes.items():
            array_size = len(attributes)
            attr_names = []
            attr_text = []

            for name, text in attributes.items():
                attr_names.append(str(name).encode(self.encoding))
                attr_text.append(str(text).encode(self.encoding))

            attr_names = (c_char_p * array_size)(*attr_names)
            attr_text = (c_char_p * array_size)(*attr_text)

            func.argtypes = [
                c_int,
                c_char_p,
                POINTER(c_char_p * array_size),
                POINTER(c_char_p * array_size),
                c_int,
            ]

            retcode = func(
                self.fh, var_name.encode(self.encoding), attr_names, attr_text, array_size
            )
            warn_or_raise(retcode, func, var_name)

    def _get_var_compat_name(self, var_name):
        "Returns 8 byte compatible variable name"

        func = self.spssio.spssGetVarCompatName
        func.argtypes = [c_int, c_char_p, c_char_p]

        var_compat_name = create_string_buffer(SPSS_MAX_SHORTVARNAME + 1)
        retcode = func(self.fh, var_name.encode(self.encoding), var_compat_name)
        warn_or_raise(retcode, func, var_name)

        return var_compat_name.value.decode(self.encoding).strip()

    @property
    def var_compat_names(self):
        """Returns dictionary of variable names with their compatible 8 byte name counterparts"""

        var_compat_names = {}
        for var_name in self.var_names:
            var_compat_names[var_name] = self._get_var_compat_name(var_name)

        return var_compat_names

    @property
    def var_sets(self):
        """Get or set variable sets

        SPSS apparently may use the 8 byte compatible variable names for this property.
        It's currently not possible to obtain the auto-generated compatible names
        until the dictionary is committed, which means setting this property potentially
        requires first comitting a dictionary with all variables, and then rewriting it
        after obtaining the compatible variable names.

        Set names when created in the normal SPSS application allow spaces and special characters.
        However, The I/O module returns an SPSS_INVALID_VARSETDEF error when these are included.
        When an "=" sign is included in the set name, the set name is truncated (same behavior).
        """

        short_to_long_var_names = {
            var_compat_name: var_name
            for var_name, var_compat_name in self.var_compat_names.items()
        }

        func = self.spssio.spssGetVariableSets
        clean = self.spssio.spssFreeVariableSets

        func.argtypes = [c_int, POINTER(c_char_p)]
        var_sets_string = c_char_p()

        retcode = func(self.fh, var_sets_string)
        warn_or_raise(retcode, func)

        var_sets_dict = {}

        if retcode not in [SPSS_NO_VARSETS, SPSS_EMPTY_VARSETS]:
            var_sets = var_sets_string.value.decode(self.encoding)  # pylint: disable=no-member
            var_sets = var_sets.strip().split("\n")

            for var_set in var_sets:
                try:
                    set_name, var_list = var_set.split("=", maxsplit=1)
                except ValueError:
                    pass
                else:
                    var_list = var_list.strip().split()
                    var_sets_dict[set_name] = [
                        short_to_long_var_names.get(var, var) for var in var_list
                    ]

        retcode = clean(var_sets_string)
        warn_or_raise(retcode, clean)

        return var_sets_dict

    @var_sets.setter
    def var_sets(self, var_sets):
        if not var_sets:
            return

        func = self.spssio.spssSetVariableSets
        func.argtypes = [c_int, c_char_p]

        var_set_defs = []

        for set_name, var_list in var_sets.items():
            set_name_fixed = set_name if "=" not in set_name else set_name[: set_name.find("=")]
            var_list_string = " ".join(var_list)
            var_set_defs.append(f"{set_name_fixed}= {var_list_string}")

        var_sets_string = "\n".join(var_set_defs)

        retcode = func(self.fh, var_sets_string.encode(self.encoding))
        warn_or_raise(retcode, func)

    def commit_header(self):
        """Function to finalize metadata before writing data values

        Once this function is called, no further metadata modification is allowed
        """

        func = self.spssio.spssCommitHeader
        retcode = func(self.fh)
        warn_or_raise(retcode, func)
