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

from ctypes import (Structure, 
                    byref, POINTER, create_string_buffer,
                    c_int, c_long, c_double, 
                    c_char, c_char_p)

from constants import (retcodes,
                       spss_formats_simple,
                       spss_formats_simple_rev,
                       max_lengths,
                       measure_levels,
                       measure_levels_str,
                       alignments,
                       alignments_str,
                       roles,
                       roles_str)

from spssfile import SPSSFile

  


def varFormat_to_varFormatTuple(varFormat):
    if isinstance(varFormat, (tuple, list)):
        return varFormat

    varFormat = varFormat.upper() + '.0'

    loc = -1
    for i, ch in enumerate(varFormat):
        if ch.isdigit():
            loc = i
            break

    fType = spss_formats_simple_rev[varFormat[:loc]]
    fWidth = int(varFormat[loc:].split('.')[0])
    fDec = int(varFormat[loc:].split('.')[1])
     
    return (fType, fWidth, fDec)    





class Header(SPSSFile):
        
    def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       

    @property
    def fileAttributes(self):
        """Get or set file attributes"""

        func = self.spssio.spssGetFileAttributes
        def func_config(array_size=0):            
            argtypes = [c_int, 
                        POINTER(POINTER(c_char_p * array_size)), 
                        POINTER(POINTER(c_char_p * array_size)), 
                        POINTER(c_int)]
            attribNames = POINTER(c_char_p * array_size)()
            attribText = POINTER(c_char_p * array_size)()
            nAttributes = c_int()
            return argtypes, attribNames, attribText, nAttributes
        
        # first get initial size
        argtypes, attribNames, attribText, nAttributes = func_config()
        func.argtypes = argtypes
        retcode = func(self.fh, attribNames, attribText, nAttributes)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
        
        # get actual array size and clean
        array_size = nAttributes.value
        self.spssio.spssFreeAttributes(attribNames, attribText, nAttributes)
        
        if array_size == 0:
            return {}
        
        else:
            # get attributes
            argtypes, attribNames, attribText, nAttributes = func_config(array_size)
            func.argtypes = argtypes
            retcode = func(self.fh, attribNames, attribText, nAttributes)
            if retcode > 0:
                raise Exception(retcodes.get(retcode))
                
            # clean
            self.spssio.spssFreeAttributes(attribNames, attribText, nAttributes)  
            
            attribNames = (x.decode(self.encoding) for x in attribNames[0])
            attribText = (x.decode(self.encoding) for x in attribText[0])                              
        
            return dict(zip(attribNames, attribText))
        
    @fileAttributes.setter
    def fileAttributes(self, attributes):
        array_size = len(attributes)
        aName = []
        aText = []
                
        for name, text in attributes.items():
            aName.append(str(name).encode(self.encoding))
            aText.append(str(text).encode(self.encoding))
            
        attribNames = (c_char_p * array_size)(*aName)
        attribText = (c_char_p * array_size)(*aText)
        
        func = self.spssio.spssSetFileAttributes
        func.argtypes = [c_int, 
                         POINTER(c_char_p * array_size), 
                         POINTER(c_char_p * array_size), 
                         c_int]
        
        retcode = func(self.fh, attribNames, attribText, array_size)
        
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
    

    @property
    def varNames(self):
        numVars = self.varCount
        
        func = self.spssio.spssGetVarNames        
        func.argtypes = [c_int, 
                         POINTER(c_int), 
                         POINTER(POINTER(c_char_p * numVars)), 
                         POINTER(POINTER(c_int * numVars))]         
        
        _numVars = c_int()
        varNames = POINTER(c_char_p * numVars)()
        varTypes = POINTER(c_int * numVars)()       
        
        retcode = func(self.fh, _numVars, varNames, varTypes)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
        else:
            varNameList = [varNames[0][i].decode(self.encoding) for i in range(numVars)]
            self.spssio.spssFreeVarNames(varNames, varTypes, _numVars)
            return varNameList
        
    @property
    def varTypes(self):
        numVars = self.varCount
        
        func = self.spssio.spssGetVarNames        
        func.argtypes = [c_int, 
                         POINTER(c_int), 
                         POINTER(POINTER(c_char_p * numVars)), 
                         POINTER(POINTER(c_int * numVars))]         
        
        _numVars = c_int()
        varNames = POINTER(c_char_p * numVars)()
        varTypes = POINTER(c_int * numVars)()       
        
        retcode = func(self.fh, _numVars, varNames, varTypes)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
        else:
            varTypesDict = {varNames[0][i].decode(self.encoding): varTypes[0][i] for i in range(numVars)}
            self.spssio.spssFreeVarNames(varNames, varTypes, _numVars)
            return varTypesDict 
        
    @varTypes.setter
    def varTypes(self, varTypes):
        for varName, varType in varTypes.items():
            self._addVar(varName, varType)
                  
    def _addVar(self, varName, varType=0):
        func = self.spssio.spssSetVarName
        func.argtypes = [c_int, c_char_p, c_int]
        retcode = func(self.fh, varName.encode(self.encoding), c_int(varType))
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
            
    def _getVarHandle(self, varName):
        func = self.spssio.spssGetVarHandle
        func.argtypes = [c_int, c_char_p, POINTER(c_double)]
        
        varHandle = c_double()
        retcode = func(self.fh, varName.encode(self.encoding), varHandle)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
        else:
            return varHandle
            
    @property
    def varHandles(self):
        func = self.spssio.spssGetVarHandle
        func.argtypes = [c_int, c_char_p, POINTER(c_double)]
        
        varHandles = {}
        for varName in self.varNames:
            varHandle = c_double()
            retcode = func(self.fh, varName.encode(self.encoding), varHandle)
            if retcode > 0:
                raise Exception(retcodes.get(retcode))
            else:
                varHandles[varName] = varHandle
                
        return varHandles
    
    def _getVarFormat(self, varName):
        func = self.spssio.spssGetVarPrintFormat
        func.argtypes = [c_int, c_char_p, POINTER(c_int), POINTER(c_int), POINTER(c_int)]
        
        fType = c_int()
        fDec = c_int()
        fWidth = c_int()
        retcode = func(self.fh, varName.encode(self.encoding), fType, fDec, fWidth)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
        else:
            return (fType.value, fWidth.value, fDec.value)
  
    @property
    def varFormatsTuple(self):
        """Get variable formats in tuple style (Type, Width, Decimals)
            
        ex. (5, 8, 2) instead of F8.2       
        """

        varFormats = {}
        for varName in self.varNames:
            varFormats[varName] = self._getVarFormat(varName)
        return varFormats
            
    @property
    def varFormats(self):
        """Get or set variable formats

        Parameters
        ----------
        varFormats : dict
            Dictionary of variable names and formats (normal or tuple)

        Returns
        -------
        dict
            Dictionary of variable names and formats (normal)

        Use varFormatsTuple property to get formats in tuple style
        """

        varFormats = {}
        for varName in self.varNames:
            fType, fWidth, fDec = self._getVarFormat(varName)
            varFormats[varName] = spss_formats_simple[fType] + str(int(fWidth)) + ('.' + str(int(fDec)) if fDec else '')
        return varFormats

       
    @varFormats.setter
    def varFormats(self, varFormats):
        varNames = self.varNames

        for varName, varFormat in varFormats.items():
            if varName in varNames:
                
                # convert to tuple in case string type is supplied
                varFormat = varFormat_to_varFormatTuple(varFormat)

                fType, fWidth, fDec = varFormat
                
                for func in (self.spssio.spssSetVarPrintFormat, self.spssio.spssSetVarWriteFormat):
                    func.argtypes = [c_int, c_char_p, c_int, c_int, c_int]
                    retcode = func(self.fh, varName.encode(self.encoding), c_int(fType), c_int(fDec), c_int(fWidth))
                    if retcode > 0:
                        raise Exception(str(retcodes.get(retcode)) + ': ' + varName + ' - ' + str(varFormat))
    
    @property
    def varMeasureLevels(self):
        """Get or set variable measure levels

        0 = Unknown
        1 = Nominal
        2 = Ordinal
        3 = Scale
        """

        func = self.spssio.spssGetVarMeasureLevel
        func.argtypes = [c_int, c_char_p, POINTER(c_int)]
        
        varLevels = {}
        for varName in self.varNames:
            level = c_int()
            retcode = func(self.fh, varName.encode(self.encoding), level)
            if retcode > 0:
                raise Exception(retcodes.get(retcode))
            varLevels[varName] = measure_levels_str[level.value]
        return varLevels
        
    @varMeasureLevels.setter
    def varMeasureLevels(self, varMeasureLevels):
        varNames = self.varNames
        
        func = self.spssio.spssSetVarMeasureLevel
        func.argtypes = [c_int, c_char_p, c_int]
        
        for varName, measureLevel in varMeasureLevels.items():
            measureLevel = measure_levels.get(str(measureLevel).lower(), measureLevel)
            if varName in varNames:
                retcode = func(self.fh, varName.encode(self.encoding), c_int(measureLevel))
                if retcode > 0:
                    raise Exception(retcodes.get(retcode))
    
    @property
    def varAlignments(self):
        """ Get or set variable alignments

        0 = SPSS_ALIGN_LEFT
        1 = SPSS_ALIGN_RIGHT
        2 = SPSS_ALIGN_CENTER
        """

        func = self.spssio.spssGetVarAlignment
        func.argtypes = [c_int, c_char_p, POINTER(c_int)]
        
        alignments = {}
        for varName in self.varNames:
            alignment = c_int()
            retcode = func(self.fh, varName.encode(self.encoding), alignment)
            if retcode > 0:
                raise Exception(retcodes.get(retcode))
            alignments[varName] = alignments_str[alignment.value]
        return alignments
    
    @varAlignments.setter
    def varAlignments(self, varAlignments):
        varNames = self.varNames
        
        func = self.spssio.spssSetVarAlignment
        func.argtypes = [c_int, c_char_p, c_int]
        
        for varName, alignment in varAlignments.items():
            alignment = alignments.get(str(alignment).lower(), alignment)
            if varName in varNames:
                retcode = func(self.fh, varName.encode(self.encoding), alignment)
                if retcode > 0:
                    raise Exception(retcodes.get(retcode))
    
    @property
    def varColumnWidths(self):
        """ Get or set column widths

        0 = Auto
        """

        func = self.spssio.spssGetVarColumnWidth
        func.argtypes = [c_int, c_char_p, POINTER(c_int)]
        
        widths = {}
        for varName in self.varNames:
            columnWidth = c_int()
            retcode = func(self.fh, varName.encode(self.encoding), columnWidth)
            if retcode > 0:
                raise Exception(retcodes.get(retcode))
            widths[varName] = columnWidth.value
        return widths
    
    @varColumnWidths.setter
    def varColumnWidths(self, varColunWidths):
        varNames = self.varNames
        
        func = self.spssio.spssSetVarColumnWidth
        func.argtypes = [c_int, c_char_p, c_int]
        
        for varName, columnWidth in varColunWidths.items():
            if varName in varNames:
                retcode = func(self.fh, varName.encode(self.encoding), columnWidth)
                if retcode > 0:
                    raise Exception(retcodes.get(retcode))
    
    @property
    def varLabels(self):        
        lenBuff = max_lengths['SPSS_MAX_VARLABEL'] + 1
        buffer = create_string_buffer(lenBuff)
               
        func = self.spssio.spssGetVarLabelLong
        func.argtypes = [c_int, c_char_p, c_char_p, c_int, POINTER(c_int)]       
        
        varLabels = {}
        for var in self.varNames:
            varName = var.encode(self.encoding)            
            lenLabel = c_int()
            retcode = func(self.fh, varName, buffer, lenBuff, lenLabel)
            if retcode > 0:
                raise Exception(retcodes.get(retcode))
            else:
                varLabels[var] = buffer.value.decode(self.encoding)            
        return varLabels
           
    @varLabels.setter
    def varLabels(self, labels):
        varNames = self.varNames
        
        func = self.spssio.spssSetVarLabel
        func.argtypes = [c_int, c_char_p, c_char_p]
        
        for varName, varLabel in labels.items():
            if varName in varNames:
                retcode = func(self.fh, varName.encode(self.encoding), varLabel.encode(self.encoding))
                if retcode > 0:
                    raise Exception(retcodes.get(retcode))
                
    @property
    def varRoles(self):
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
        
        varRoles = {}
        for varName in self.varNames:
            role = c_int()
            retcode = func(self.fh, varName.encode(self.encoding), role)
            if retcode > 0:
                raise Exception(retcodes.get(retcode))
            else:
                varRoles[varName] = roles_str[role.value]
                
        return varRoles
            
    @varRoles.setter
    def varRoles(self, varRoles):
        varNames = self.varNames
        func = self.spssio.spssSetVarRole
        func.argtypes = [c_int, c_char_p, c_int]
        
        for varName, role in varRoles.items():
            role = roles.get(str(role).lower(), role)
            if varName in varNames:
                retcode = func(self.fh, varName.encode(self.encoding), role)
                if retcode > 0:
                    raise Exception(retcodes.get(retcode))
                
            
    def _getVarNValueLabels(self, var):        
        func = self.spssio.spssGetVarNValueLabels
        
        def func_config(var, size=0):        
            argtypes = [c_int, c_char_p, POINTER(POINTER(c_double * size)), POINTER(POINTER(c_char_p * size)), POINTER(c_int)]        
            varName = var.encode(self.encoding)
            valuesArr = POINTER((c_double * size))()
            labelsArr = POINTER((c_char_p * size))()
            numLabels = c_int()
            return argtypes, varName, valuesArr, labelsArr, numLabels
                     
        # initial function call to get number of labels
        argtypes, varName, valuesArr, labelsArr, numLabels = func_config(var)
        func.argtypes = argtypes                
        retcode = func(self.fh, varName, valuesArr, labelsArr, numLabels)
        if retcode > 0:
            self.spssio.spssFreeVarNValueLabels(valuesArr, labelsArr, numLabels)
            raise Exception(retcodes.get(retcode))
        elif numLabels.value > 0:
            # if function call was successful and variable has value labels
            argtypes, varName, valuesArr, labelsArr, numLabels = func_config(var, numLabels.value)
            func.argtypes = argtypes
            retcode = func(self.fh, varName, valuesArr, labelsArr, numLabels)
            valueLabels = {valuesArr[0][i]: labelsArr[0][i].decode(self.encoding) for i in range(numLabels.value)}
            self.spssio.spssFreeVarNValueLabels(valuesArr, labelsArr, numLabels)            
            return valueLabels
        else:
            return {}

    def _getVarCValueLabels(self, var):        
        func = self.spssio.spssGetVarCValueLabels
        
        def func_config(var, size=0):        
            argtypes = [c_int, c_char_p, POINTER(POINTER(c_char_p * size)), POINTER(POINTER(c_char_p * size)), POINTER(c_int)]        
            varName = var.encode(self.encoding)
            valuesArr = POINTER((c_char_p * size))()
            labelsArr = POINTER((c_char_p * size))()
            numLabels = c_int()
            return argtypes, varName, valuesArr, labelsArr, numLabels
                     
        # initial function call to get number of labels
        argtypes, varName, valuesArr, labelsArr, numLabels = func_config(var)
        func.argtypes = argtypes                
        retcode = func(self.fh, varName, valuesArr, labelsArr, numLabels)
        if retcode > 0:
            self.spssio.spssFreeVarCValueLabels(valuesArr, labelsArr, numLabels)
            raise Exception(retcodes.get(retcode))
        elif numLabels.value > 0:
            # if function call was successful and variable has value labels
            argtypes, varName, valuesArr, labelsArr, numLabels = func_config(var, numLabels.value)
            func.argtypes = argtypes
            retcode = func(self.fh, varName, valuesArr, labelsArr, numLabels)
            valueLabels = {valuesArr[0][i].decode(self.encoding).rstrip(): labelsArr[0][i].decode(self.encoding) for i in range(numLabels.value)}
            self.spssio.spssFreeVarCValueLabels(valuesArr, labelsArr, numLabels)            
            return valueLabels
        else:
            return {}        
            
        
    @property
    def varValueLabels(self):
        """Get or set value labels
        
        Note: value labels are only included for numeric variables or string variables w/ length <= 8
        """

        varValueLabels = {}
        for varName, varType in self.varTypes.items():
            if varType == 0:
                varValueLabels[varName] = self._getVarNValueLabels(varName)
            elif varType <= 8:
                varValueLabels[varName] = self._getVarCValueLabels(varName)
        return {k:v for k,v in varValueLabels.items() if v}
    
    
    def _setVarNValueLabel(self, varName, value, label):
        func = self.spssio.spssSetVarNValueLabel
        func.argtypes = [c_int, c_char_p, c_double, c_char_p]
        retcode = func(self.fh, varName.encode(self.encoding), c_double(value), label.encode(self.encoding))
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
            
    
    def _setVarCValueLabel(self, varName, value, label):
        func = self.spssio.spssSetVarCValueLabel
        func.argtypes = [c_int, c_char_p, c_char_p, c_char_p]
        retcode = func(self.fh, varName.encode(self.encoding), value.encode(self.encoding), label.encode(self.encoding))
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
    
    @varValueLabels.setter
    def varValueLabels(self, varValueLabels):
        varTypes = self.varTypes       
        for varName, valueLabels in varValueLabels.items():
            varType = varTypes.get(varName)
            if varType is not None:
                if varType:
                    func = self._setVarCValueLabel
                else:
                    func = self._setVarNValueLabel
                for value, label in valueLabels.items():
                    func(varName, value, label)
     
    @property
    def multRespDefs(self):
        mrsets_dict = {}
        
        func = self.spssio.spssGetMultRespDefs
        func.argtypes = [c_int, POINTER(c_char_p)]
        mrsets_string = c_char_p()
        retcode = func(self.fh, mrsets_string)
        if retcode > 0:
            self.spssio.spssFreeMultRespDefs(mrsets_string)
            raise Exception(retcodes.get(retcode))
        elif mrsets_string:
            mrsets = mrsets_string.value.decode(self.encoding).strip().split('\n')
            mrsets = [x.split('=', 2) for x in mrsets]                
            for mrset in mrsets:
                d = {}
                setname, attr = mrset
                if attr[0].upper() == 'D':
                    d['type'] = 'D'
                    idx = 1
                    d['value_length'] = attr[idx:].split(' ', 1)[0]
                    idx += (len(d['value_length']) + 1)
                    d['counted_value'] = attr[idx:][:int(d['value_length'].strip())]
                    idx += (len(d['counted_value']) + 1)
                    d['label_length'] = attr[idx:].split(' ', 1)[0]
                    idx += (len(d['label_length']) + 1)
                    d['label'] = attr[idx:][:int(d['label_length'].strip())]
                    idx += (len(d['label']) + 1)
                    d['variable_list'] = attr[idx:].split()
                    mrsets_dict[setname] = d
                elif attr[0].upper() == 'C':
                    d['type'] = 'C'
                    idx = 2
                    d['value_length'], d['counted_value'] = None, None
                    d['label_length'] = attr[idx:].split(' ', 1)[0]
                    idx += (len(d['label_length']) + 1)
                    d['label'] = attr[idx:][:int(d['label_length'].strip())]
                    idx += (len(d['label']) + 1)
                    d['variable_list'] = attr[idx:].split()
                    mrsets_dict[setname] = d     
            
        # clean
        self.spssio.spssFreeMultRespDefs(mrsets_string)        
            
        if len(mrsets_dict):
            varTypes = self.varTypes
            for mrset, d in mrsets_dict.items():
                d['label_length'] = int(d['label_length'])
                if d['value_length'] is not None:
                    d['value_length'] = int(d['value_length'])
                if d['counted_value'] is not None and varTypes[d['variable_list'][0]] == 0:
                    d['counted_value'] = int(d['counted_value'])    
            
        return mrsets_dict
    
    @multRespDefs.setter        
    def multRespDefs(self, multRespDefs):
        """Get or set multiple response set definitions

        Returns
        -------
        dict
            setName
                - type : str ('C' or 'D')
                - counted_value : int or str (for 'D' type only)
                - label : str
                - variable_list : list of variables included in set
        """

        varTypes = self.varTypes
        
        # prepare mrsets
        mrset_list = []
        for mrset, d in multRespDefs.items():
            if mrset[0] != '$':
                mrset = '$' + mrset
            label = str(d.get('label', mrset[1:]))
            label_length = str(len(label.encode(self.encoding)))    
            set_type = d.get('type')
            
            variable_list = [var for var in d.get('variable_list', []) if var in varTypes]
            if len(variable_list):
                # only attempt to add if at least one variable is present
                if not isinstance(variable_list, (list, tuple)):
                    raise TypeError(f"Expected 'list' or 'tuple' for variable list - {mrset}")
                if set_type is None:
                    raise ValueError(f"Missing mrset 'type' for {mrset}: must be C (category) or D (dichotomous)")
                elif set_type.upper() == 'C':
                    mrset_list.append(' '.join([mrset + '=' + set_type, label_length, label, ' '.join(variable_list)]))
                elif set_type.upper() == 'D':
                    counted_value = d.get('counted_value')
                    if counted_value is None:
                        raise ValueError(f"Missing mrset 'counted_value' for {mrset}")
                    else:
                        if varTypes[variable_list[0]] == 0:
                            counted_value = int(float(counted_value))
                        counted_value = str(counted_value)
                        value_length = str(len(counted_value))
                    mrset_list.append(' '.join([mrset + '=' + set_type + value_length, counted_value, label_length, label, ' '.join(variable_list)]))
        mrsets = '\n'.join(mrset_list).encode(self.encoding)
        
        # set mrsets
        func = self.spssio.spssSetMultRespDefs
        func.argtypes = [c_int, c_char_p]
        retcode = func(self.fh, mrsets)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
    
    @property
    def caseSize(self):
        func = self.spssio.spssGetCaseSize
        func.argtypes = [c_int, POINTER(c_long)]        
        caseSize = c_long()
        retcode = func(self.fh, caseSize)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))            
        return caseSize.value
    
    @property
    def caseWeightVar(self):
        caseWeightVar = create_string_buffer(max_lengths['SPSS_MAX_VARNAME'] + 1)
        retcode = self.spssio.spssGetCaseWeightVar(self.fh, caseWeightVar)
        if retcode <= 0:
            return caseWeightVar.value.decode(self.encoding)
        
    @caseWeightVar.setter
    def caseWeightVar(self, varName):
        func = self.spssio.spssSetCaseWeightVar
        func.argtypes = [c_int, c_char_p]
        retcode = func(self.fh, varName.encode(self.encoding))
        if retcode > 0:
            raise Exception(retcodes.get(retcode))  
            
    def _getVarNMissingValues(self, var):        
        func = self.spssio.spssGetVarNMissingValues
        func.argtypes = [c_int, c_char_p, POINTER(c_int), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
                      
        missingFormat = c_int()
        val_1, val_2, val_3 = c_double(), c_double(), c_double()
        retcode = func(self.fh, var.encode(self.encoding), missingFormat, val_1, val_2, val_3)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
            
        missingFormat = missingFormat.value
        missingValues = [val_1.value, val_2.value, val_3.value] 
                  
        return (missingFormat, missingValues)
    
    def _getVarCMissingValues(self, var, varType):  
        """Will not return missing values if variable type > 8 (ex. A25)"""

        func = self.spssio.spssGetVarCMissingValues
        func.argtypes = [c_int, c_char_p, POINTER(c_int), c_char_p, c_char_p, c_char_p]
                      
        missingFormat = c_int()
        val_1 = create_string_buffer(varType + 1)
        val_2 = create_string_buffer(varType + 1)
        val_3 = create_string_buffer(varType + 1)

        retcode = func(self.fh, var.encode(self.encoding), missingFormat, val_1, val_2, val_3)
        if retcode > 0:
            raise Exception(retcodes.get(retcode))
            
        missingFormat = missingFormat.value
        missingValues = [val_1.value.decode(self.encoding).rstrip(), 
                         val_2.value.decode(self.encoding).rstrip(), 
                         val_3.value.decode(self.encoding).rstrip()]
                  
        return (missingFormat, missingValues)
    
    @property
    def varMissingValues(self):
        varMissingValues = {}        
        for varName, varType in self.varTypes.items():           
                        
            if varType:  
                missingFormat, missingValues = self._getVarCMissingValues(varName, varType)               
            else:
                missingFormat, missingValues = self._getVarNMissingValues(varName)

            if missingFormat == 0:
                varMissingValues[varName] = None
            elif missingFormat > 0:
                varMissingValues[varName] = {'values': missingValues[:missingFormat]}
            elif missingFormat < 0:
                varMissingValues[varName] = {'lo': missingValues[0],
                                             'hi': missingValues[1],
                                             'values': missingValues[2:][:abs(missingFormat)-2]}
              
        return {k:v for k,v in varMissingValues.items() if v}
    
    @varMissingValues.setter
    def varMissingValues(self, varMissingValues):
        varTypes = self.varTypes
        
        for varName, missingValues in varMissingValues.items():
            
            if varTypes.get(varName):
                func = self.spssio.spssSetVarCMissingValues
                func.argtypes = [c_int, c_char_p, c_int, c_char_p, c_char_p, c_char_p]
                discrete_values = missingValues.get('values', [])
                missingFormat = min(3, len(discrete_values))
                val_1 = '' if missingFormat < 1 else discrete_values[0]
                val_2 = '' if missingFormat < 2 else discrete_values[1]
                val_3 = '' if missingFormat < 3 else discrete_values[2]
                retcode = func(self.fh, varName.encode(self.encoding),
                               c_int(missingFormat),
                               val_1.encode(self.encoding),
                               val_2.encode(self.encoding),
                               val_3.encode(self.encoding))
                if retcode > 0:
                    raise Exception(retcodes.get(retcode)) 
            elif varTypes.get(varName) == 0:
                func = self.spssio.spssSetVarNMissingValues
                func.argtypes = [c_int, c_char_p, c_int, c_double, c_double, c_double] 
                low = missingValues.get('lo') 
                high = missingValues.get('hi')                               
                discrete_values = missingValues.get('values', [])
                if high is not None and low is not None:
                    missingFormat = max(-3, -2 - len(discrete_values))
                    val_1 = low
                    val_2 = high 
                    val_3 = self.sysmis if missingFormat == -2 else discrete_values[0]                     
                else:
                    missingFormat = len(discrete_values)
                    val_1 = self.sysmis if missingFormat < 1 else discrete_values[0]
                    val_2 = self.sysmis if missingFormat < 2 else discrete_values[1]
                    val_3 = self.sysmis if missingFormat < 3 else discrete_values[2]                  
                retcode = func(self.fh, varName.encode(self.encoding),
                               c_int(missingFormat),
                               c_double(val_1),
                               c_double(val_2),
                               c_double(val_3))
                if retcode > 0:
                    raise Exception(retcodes.get(retcode)) 
                                 
    def commitHeader(self):
        retcode = self.spssio.spssCommitHeader(self.fh)
        if retcode:
            raise Exception(retcodes.get(retcode))

           
  
                 