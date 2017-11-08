# qcasDFtest
Unit Test scripts written in Python for validation of Queensland Casino datafiles. 

Rationale: CHK01 is essentially a manual process to verify an automated procedure for generating the Casino datafiles. The current procedure involves completing CHK01 Casino Datafiles Checklist which indicates that two officers have reviewed the datafiles generated are complete and error free. This process is laborious and time consuming however it can be automated to reduce the risk of officers not correctly following processes and provide consitency for this process. 

This script attempts to complete all CHK01 process as well as thoroughly check the outgoing Casino Datafiles for formating, naming convention and sanity checking. 

To use in Windows: 
1. Modify preferences.dat file and change the following references: 

 ```
        "previous_TSLfile" : "qcas_2017_09_v02.tsl"
        "TSLfile" : "qcas_2017_10_v01.tsl"
        "PSLfile" : "qcas_2017_10_v03.psl"
        "nextMonth_PSLfile" : "qcas_2017_11_v01.psl"
        "MSLfile" :  "qcas_2017_10_v01.msl"
        "nextMonth_MSLfile" : "qcas_2017_11_v01.msl"
        
        "path_to_binimage" : "\\\\Justice.qld.gov.au\\Data\\OLGR-TECHSERV\\BINIMAGE"
        "epsig_log_file": "C:\\Users\\aceretjr\\Documents\\dev\\qcas-Datafiles-Unittest\\logs\\epsig.log",       
```
        
2. On the command prompt (in Windows) use: `py -m unittest -v`
Will run all unit test scripts. To specify a specifc unit test use: `py -m unittest test_chk01_checklist.py`

---
# Unit Test Module Details
## Module: `test_datafiles.py`
Main class (QCASTestClient) derived from unittest.TestCase, includes the following helper class files: `PSLfile`, `MSLfile`, `TSLfile` and `CacheFile`. 

The QCASTestClient includes all modules that have common test procedures. 

## Module: `test_chk01_checklist.py`
Mirrors the checks specified in CHK01 Casino Datafiles checklist, the following unit tests are performed in this test: 

#### `test_Generated_PSL_files_Differ()`
- Verifies that the two PSL files: `self.PSLfile and self.nextMonth_PSLfile` are not the same. 

#### `test_new_games_to_be_added_are_in_PSL_files()`
- Verifies if the SSANs of new games exist in both `self.PSLfile and self.nextMonth_PSLfile` files. 

#### `test_TSL_entries_exist_in_PSL_files()`
Verifies the following entry for each new game generated: 
- Game Name is less than 30 characters long
- Manufacturer ID is valid: 00, 01, 05, 07, 09, 12, 17
- PSL Year field is valid: 2017 < year < 9999
- PSL Month field is valid:  1 < valid month < 12
- PSL SSAN is valid: 150000 < SSAN < 999999999
- Number of Hashes in the PSL entry is equal to 31

#### [to be completed] `test_Games_removed_from_PSL_files()`
- Verifies that expected games removed has been identified from the PSL files. 

#### `test_One_new_game_to_be_added_in_PSL_files()`
- Verifies that the generated PSL entries for two months is created for the Random game. 
- Verifies that the PSL entries matches for two months exists in `self.PSLfile and self.nextMonth_PSLfile`

#### `test_One_old_game_to_be_added_in_PSL_files()`
- Verifies that the generated PSL entries for two months is created for the Random game. 
- Verifies that the PSL entries matches for two months exists in `self.PSLfile and self.nextMonth_PSLfile`

## Module: `test_epsig_log_files.py`
This test script verifies the expected output of the EPSIG log. 

#### `test_Epsig_Log_file()`
- Verifies the last entry of the Epsig log file
- Verifies the version of EPSIG being used (expected: v3.5)
- Verifies that the time stamp for when EPSIG last ran is reasonable (within 7 days)
- Verifies that the time stamp for when EPSIG last completed is reasonable (within 7 days)
- Verifies that the end of the Epsig Log File indicates: "with EXIT_SUCCESS"
- Verifies that the command that was used for Epsig is correct. (Correct Epsig Binary used; Correct BINIMAGE Path used: i.e. G:\; Correct Datafiles referenced, i.e. MSL file is `self.MSLfile or self.nextMonth_MSLfile`; TSL file is `self.TSLfile`; PSL file is `self.PSLfile or self.nextMonth_PSLfile`

## Module: `test_file_name_format.py`
Generic test scripts for correct file name format and conventions. 

#### `test_MSL_filename_ends_with_MSL()`
- Verifies that `self.MSLfile or self.nextMonth_MSLfile` ends with .msl

#### `test_MSL_filename_date()`
- Verifies that the month fields in `self.MSLfile or self.nextMonth_MSLfile` are not equal
- Verifies that the MSL filename month fields are not equal
3- Verifies that the MSL year fields is the same if month is less than 12, otherwise an increment in Year value is expected

#### `test_MSL_filename_version()`
- Verifies that the MSL version fields must always be `v1`

#### `test_TSLfile_ends_with_TSL()`
- Verifies that the `self.TSLfile` file ends with '.tsl'

#### `test_PSLfile_ends_with_PSL()`
- Verifies that the `self.PSLfile or self.nextMonth_PSLfile` ends with '.psl'

#### `test_PSL_file_version_increment()`
- [to be completed] Verifies that the PSL file version should be incremented if not a new moth.

#### `test_PSL_filename_date()`
- Verify that current PSL month is not equal to the new PSL month 
- Verify that the PSL year is the same, unless current PSL month is December.

## Module: `test_general_file_format.py`
#### `test_Read_PSL_file()`
- Verifies that `self.PSLfile` and `self.nextMonth_PSLfile` can be read from disk

#### `test_Read_TSL_file()`
- Verifies that `self.TSLfile` and `self.previous_TSLfile` can be read from disk

#### `test_MSL_fields()`
- Verifies `self.MSLfile` file format
- Verifies MSL file month field is this month's or next
- Verifies MSL file year field is this year's or next
- Verifies MSL file has 31 seeds

#### `test_PSL_fields()`
- Verifies `self.PSLfile` and `self.nextMonth_PSLfile` file format
- Verifies PSL file manufacturer field is valid
- Verifies PSL Game name field length is 30 characters or less
- Verifies PSL year field is this year's or next
- Verifies PSL month field is this month's or next

#### `test_TSL_fields()`
- Verifies TSL file manufacturer field entries is valid
- Verifies TSL file SSAN field is unique
- Verifies TSL file Bin Image Type is valid 

## Module: `test_PSL_files.py`
#### `test_PSL_size_is_reasonable()`
- Verifies that the file size of the PSL files is reasonable (greater than 1055KB as at July 2013)

### `test_PSL_content()`
- Verifies the `self.PSLfile` and `self.nextMonth_PSLfile` file formats
- Verifies that the PSL file has the same number of lines as the generated PSL entry

## Module: `test_MSL_files.py`
#### `test_MSL_size_is_reasonable()`
- Verifies that the file size of the MSL files is reasonable (The size should not change and is 1KB)

#### `test_MSL_content()`
- Verifies the `self.MSLfile` and `self.nextMonth_MSLfile` file formats
- Verifies that the MSL files only has one entry

#### `test_MSL_file_one_row()`
- Verifies that the MSL files only has one entry

#### `test_Read_MSL_file()`
- Verifies that the `self.MSLfile` and `self.nextMonth_MSLfile` can be read from disk 
