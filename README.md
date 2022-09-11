
## Overview

pyspssio is a python package for reading and writing SPSS (.sav and .zsav) files to/from pandas dataframes.

This package uses the I/O Module for SPSS Statistics v27 available at https://www.ibm.com/.

**WARNING**: This is an early release with limited testing. Use with caution.

## Motivation

Main reason for creating this package is to fill gaps by other similar packages.

`savReaderWriter`
 * doesn't support python > 3.5
 * not particularly user friendly

`pyreadstat`
 * doesn't read or write multi response set definitions
 * datetime conversion quirks
 * issues reading/writing long string variables ([https://github.com/Roche/pyreadstat/issues/119](https://github.com/Roche/pyreadstat/issues/119))

`pyspssio` supports recent versions of python and can read/write most SPSS file metadata properties. The `usecols` argument when reading files also accepts a callable for more flexible variable selection.


## Basic Usage


Installation

```
pip install pyspssio
```

Import

```
import pyspssio
```

### Reading

Read data and metadata

```
df, meta = pyspssio.read_sav("spss_file.sav")
```

Read metadata only

```
meta = pyspssio.read_metadata("spss_file.sav")
```

Read data in chunks of `chunksize` (number of rows/records)

```
for df in pyspssio.read_sav("spss_file.sav", chunksize=1000):
#   do something
```

Note: metadata is not returned when reading in chunks


### Writing

Write dataframe to file.

```
pyspssio.write_sav("spss_file.sav", df)
```

### Appending

Append existing SPSS file with new records.

```
pyspssio.write_sav("spss_file.sav", df)
```

Note: Cannot modify metadata when appending new records. Be careful with strings that might be longer than the already defined width as they may be automatically truncated without warning.


## Other Notes

### Date/Time Variables

**Date and datetime variables** - These are converted to/from full datetime objects, even for formats like DATE, QYR, and WKYR which don't display a time component. Users can opt to use Pandas' `.dt` accessor to extract specific components or force a specific accuracy (e.g., minute, day, hour) after reading the data (ex. [`.dt.floor`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.dt.floor.html)). The `var_formats` and/or `var_formats_tuple` metadata attributes can be used to see the original SPSS formats.

**Time variables** - These are converted to/from timestamp objects.

Python/Pandas stores datetimes in nanseconds while SPSS stores them in seconds. Due to conversions that must take place, there may be some small (ms) discrepancies between an original dataframe used to write an SPSS file and a dataframe read back from the same SPSS file.


## I/O Module Procedures

List of available I/O module procedures and class for which they fall under. See official documentation for details on each one.

Some of these procedures are implemented as hidden methods referenced within a more generalized function/property. For example, instead of calling `spssSetVarLabel` manually for each variable, users should assign all variable labels at once by setting `self.var_labels = {var1: label1, var2: label2, ...}`.

All I/O module procedures can be accessed directly with `self.spssio.[procedure]`.


### SPSSFile

spssOpenRead

spssCloseRead

spssOpenWrite

spssCloseWrite

spssOpenAppend

spssCloseAppend

spssHostSysmisVal

spssLowHighVal

spssSetLocale

spssGetInterfaceEncoding

spssSetInterfaceEncoding

spssGetFileEncoding

spssIsCompatibleEncoding

spssGetCompression

spssSetCompression

spssGetReleaseInfo

spssGetNumberofCases

spssGetNumberofVariables


### Header

spssGetFileAttributes

spssSetFileAttributes

spssGetVarNames

spssSetVarName

spssGetVarHandle

spssGetVarPrintFormat

spssSetVarPrintFormat

spssSetVarWriteFormat

spssGetVarMeasureLevel

spssSetVarMeasureLevel

spssGetVarAlignment

spssSetVarAlignment

spssGetVarColumnWidth

spssSetVarColumnWidth

spssGetVarLabelLong

spssSetVarLabel

spssGetVarRole

spssSetVarRole

spssGetVarCValueLabels

spssSetVarCValueLabel

spssGetVarNValueLabels

spssSetVarNValueLabel

spssGetVarCMissingValues

spssSetVarCMissingValues

spssGetVarNMissingValues

spssSetVarNMissingValues

spssGetMultRespDefs

spssSetMultRespDefs

spssGetCaseSize

spssGetCaseWeightVar

spssSetCaseWeightVar

spssGetVarAttributes

spssSetVarAttributes

spssGetVarCompatName

spssGetVariableSets

spssSetVariableSets

spssCommitHeader


### Reader

spssSeekNextCase

spssWholeCaseIn


### Writer

spssWholeCaseOut

spssSetValueChar

spssSetValueNumeric

spssCommitCaseRecord


### Not Implemented (yet)

spssAddMultRespDefC

spssAddMultRespDefExt

spssAddMultRespDefN

spssGetMultRespCount

spssGetMultRespDefByIndex

spssGetMultRespDefsEx

spssConvertDate - manual conversion instead

spssConvertSPSSDate - manual conversion instead

spssConvertSPSSTime - manual conversion instead

spssConvertTime - manual conversion instead

spssCopyDocuments

spssGetDEWFirst

spssGetDEWGUID

spssGetDewInfo

spssGetDEWNext

spssSetDEWFirst

spssSetDEWGUID

spssSetDEWNext

spssGetDateVariables

spssGetEstimatedNofCases

spssGetFileAttribute - uses spssGetFileAttributes instead

spssGetFileCodePage

spssGetIdString

spssGetSystemString

spssGetTextInfo

spssGetTimeStamp

spssGetValueChar - uses spssWholeCaseIn instead

spssGetValueNumeric - uses spssWholeCaseIn instead

spssAddVarAttribute - uses spssSetVarAttributes instead

spssGetVarCValueLabel - uses spssGetVarCValueLabels instead

spssGetVarCValueLabelLong - uses spssGetVarCValueLabels instead

spssGetVarInfo

spssGetVarLabel - uses spssGetVarLabelLong instead

spssGetVarNValueLabel - uses spssGetVarNValueLabels instead

spssGetVarNValueLabelLong - uses spssGetVarNValueLabels instead

spssGetVarWriteFormat - uses spssGetVarPrintFormat instead (print/write formats tied together)

spssOpenAppendEx

spssOpenReadEx

spssOpenWriteCopy

spssOpenWriteCopyEx

spssOpenWriteCopyExDict

spssOpenWriteCopyExFile

spssOpenWriteEx

spssQueryType7

spssReadCaseRecord - uses spssWholeCaseIn instead

spssSetDateVariables

spssSetIdString

spssSetTempDir

spssSetTextInfo

spssSetVarCValueLabels - uses spssSetVarCValueLabel instead

spssSetVarNValueLabels - uses spssSetVarNValueLabel instead

spssSysmisVal - uses spssHostSysmisVal instead

spssValidateVarname

