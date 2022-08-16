
pyspssio
========================  

Python package for reading and writing SPSS (.sav and .zsav) files to/from pandas dataframes.  

This package uses the I/O Module for SPSS Statistics v27 available at https://www.ibm.com/.

**WARNING**: This is an early release with limited testing. Use with caution.

Motivation  
========================  

Main reason for creating this package is to fill gaps by other similar packages.  

`savReaderWriter`  
 * doesn't support python > 3.5  
   
`pyreadstat`   
 * doesn't read or write multiple response set definitions  
 * datetime conversion quirks  
 * issues reading/writing long string variables (https://github.com/Roche/pyreadstat/issues/119)  

`pyspssio` supports recent versions of python and can read/write most SPSS file metadata properties. The `usecols` argument when reading files also accepts a callable for more flexible variable selection.  


Basic Usage  
========================  


Installation

```  
pip install pyspssio  
```  

Import  

```  
import pyspssio  
```  


Reading  
------------------------  

Read data and metadata  

```  
df, meta = pyspssio.read_sav('spss_file.sav')  
```  

Read metadata only  

```
meta = pyspssio.read_metadata('spss_file.sav')
```

Read data in chunks of `chunksize` (number of rows/records)  

```  
for df in pyspssio.read_sav('spss_file.sav', chunksize=1000):  
#   do something   
```  

Note: metadata is not returned when reading in chunks  

Optional arguments:  
 * **row_offset** - row number to start at (0-indexed)  
 * **row_limit** - maximum number of rows to return  
 * **usecols** - columns/variables to read (str, tuple, list, callable)  
 * **convert_datetimes** - (True - default) to convert SPSS date, time, datetime variables to python/pandas datetime (default True)  
 * **include_user_missing** - (True - default) keep user missing values in the dataframe or (False) replace with '' (strings) or NaN (numeric)  
 * **chunksize** - chunksize to read in chunks (if defined returns generator object)  
 * **set_locale** - Set I/O locale (e.g., 'English_United States.1252') when operating in codepage mode 
 * **string_nan** - define how empty strings should be returned  

Note: Datetime conversions only convert the raw SPSS value, which is always a full datetime. If only certain portions are needed (e.g., date, time, year, month, day, etc.), use the `.dt` accessor on that column. The `varFormats` or `varFormatsTuple` metadata attributes can be used to see the original SPSS formats.  


Writing  
------------------------   

Write dataframe to file.  

```  
pyspssio.write_sav(`spss_file.sav`, df)  
```  

Optional arguments:  
 * **unicode** - (True - default) for 'UTF-8' or (False) for codepage mode  
 * **set_locale** - Set I/O locale (e.g., 'English_United States.1252') when operating in codepage mode  
 * **metadata** - dictionary of metadata properties and their values (e.g., varLabels, varValueLabels, multRespDefs, etc.)  
 * **kwargs** - can pass metadata properties as separate arguments; these take precedence over those passed through the metadata argument  


Appending  
------------------------   

Append existing SPSS file with new records.

```  
pyspssio.write_sav(`spss_file.sav`, df)  
```  

Optional arguments:  
 * **set_locale** - Set I/O locale (e.g., 'English_United States.1252') when operating in codepage mode   
  
Note: Cannot modify metadata when appending new records. Be careful with strings that might be longer than the allowed width. 


I/O Module Procedures  
========================  

List of available I/O module procedures and class for which they fall under. See official documentation for details on each one.  

Some of these procedures are implemented as hidden methods referenced within a more generalized function/property.  

For example, instead of calling `spssSetVarLabel` manually for each variable, users should assign all variable labels at once by setting `self.varLabels = {var1: label1, var2: label2, ...}`.   

All of the I/O module procedures can be accessed directly with `self.spssio.[procedure]`.  


SpssFile  
------------------------  

spssOpenRead    

spssCloseRead    

spssOpenWrite   
 
spssCloseWrite    

spssOpenAppend   
 
spssCloseAppend    

spssHostSysmisVal    

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


Header  
------------------------  

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

spssCommitHeader  


Reader  
------------------------  

spssSeekNextCase  

spssWholeCaseIn  


Writer  
------------------------  

spssWholeCaseOut  

spssSetValueChar   

spssSetValueNumeric   

spssCommitCaseRecord   


Not Implemented (yet)  
------------------------  

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

spssAddVarAttribute  

spssGetVarAttributes  

spssGetVarCompatName  

spssGetVarCValueLabel - uses spssGetVarCValueLabels instead  

spssGetVarCValueLabelLong - uses spssGetVarCValueLabels instead  

spssGetVariableSets  

spssGetVarInfo  

spssGetVarLabel - uses spssGetVarLabelLong instead  

spssGetVarNValueLabel - uses spssGetVarNValueLabels instead  

spssGetVarNValueLabelLong - uses spssGetVarNValueLabels instead  

spssGetVarWriteFormat - uses spssGetVarPrintFormat instead (print/write formats tied together)  

spssLowHighVal  

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

spssSetVarAttributes  

spssSetVarCValueLabels - uses spssSetVarCValueLabel instead  

spssSetVariableSets  

spssSetVarNValueLabels - uses spssSetVarNValueLabel instead  

spssSysmisVal - uses spssHostSysmisVal instead  

spssValidateVarname  

