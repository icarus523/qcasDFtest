# qcasDFtest
Unit Test scripts written in Python for validation of Queensland Casino datafiles. 

Rationale: CHK01 is essentially a manual process to verify an automated procedure for generating the Casino datafiles. The current procedure involves completing CHK01 Casino Datafiles Checklist which indicates that two officers have reviewed the datafiles generated are complete and error free. This process is laborious and time consuming however it can be automated to reduce the risk of officers not correctly following processes and provide consitency for this process. 

This script attempts to complete all CHK01 process as well as thoroughly check the outgoing Casino Datafiles for formating, naming convention and sanity checking. 

To use in Windows: 
1. Modify test_datafiles.py script by changing the following references: 

 ```
        # TSL files 
        self.previous_TSLfile = "qcas_2017_09_v02.tsl"
        self.TSLfile = "qcas_2017_10_v01.tsl"
        # PSL files (hashes)
        self.PSLfile = "qcas_2017_10_v03.psl"
        self.nextMonth_PSLfile = "qcas_2017_11_v01.psl"
        # MSL files (seeds)
        self.MSLfile = "qcas_2017_10_v01.msl"
        self.nextMonth_MSLfile = "qcas_2017_11_v01.msl"
```
        
2. On the command prompt (in Windows) use: `py -m unittest -v`
Will run all unit test scripts. To specify a specifc unit test use: `py -m unittest test_chk01_checklist.py`

---
# Unit Test Module Details
## `test_datafiles.py`
Main class (QCASTestClient) derived from unittest.TestCase, includes the following helper class files: `PSLfile`, `MSLfile`, `TSLfile` and `CacheFile`. 

The QCASTestClient includes all modules that have common test procedures. 

## `test_chk01_checklist.py`
Mirrors the checks specified in CHK01 Casino Datafiles checklist, the following unit tests are performed in this test: 

#### `test_Generated_PSL_files_Differ()`
Check that the two PSL files: `self.PSLfile and self.nextMonth_PSLfile` are not the same. 

#### `test_new_games_to_be_added_are_in_PSL_files()`
Confirms if the SSANs of new games exist in both `self.PSLfile and self.nextMonth_PSLfile` files. 

#### `test_TSL_entries_exist_in_PSL_files()`
Generates a list of new games based on the current TSL file

Generates a PSL entry for each item in the list of new games, for the current and next month (using the `self.MSLfile and self.nextMonth_PSLfile`) and compares it to the entries generated in the `self.PSLfile and self.nextMonth_PSLfile`. 

Verifies the following entry for each new game generated: 
- Game Name is less than 30 characters long
- Manufacturer ID is valid: 00, 01, 05, 07, 09, 12, 17
- PSL Year field is valid: 2017 < year < 9999
- PSL Month field is valid:  1 < valid month < 12
- PSL SSAN is valid: 150000 < SSAN < 999999999
- Number of Hashes in the PSL entry is equal to 31

#### `test_Games_removed_from_PSL_files()`
Generates a difference from previous month PSL and this Months PSL files 

Verifies that expected games removed has been identified from the PSL files. 

#### `test_One_new_game_to_be_added_in_PSL_files()`
Selects one new game randomly to be added into the PSL files, and then generates the PSL entry using the MSL files (two months). 

Verifies that the generated PSL entries for two months is created for the Random game. 

Verifies that the PSL entries matches for two months exists in `self.PSLfile and self.nextMonth_PSLfile`

#### `test_One_old_game_to_be_added_in_PSL_files()`
Selects a Random game from the complete TSL file (SHA1 or BLNK only) and then generates the PSL entry using the MSL files (two months). 

Verifies that the generated PSL entries for two months is created for the Random game. 

Verifies that the PSL entries matches for two months exists in `self.PSLfile and self.nextMonth_PSLfile`

## `test_epsig_log_files.py`
This test script verifies the expected output of the EPSIG log. 

#### `test_Epsig_Log_file()`
- Verifies the last entry of the Epsig log file
- Verifies the version of EPSIG being used (expected: v3.5)
- Verifies that the time stamp for when EPSIG last ran is reasonable (within 7 days)
- Verifies that the time stamp for when EPSIG last completed is reasonable (within 7 days)
- Verifies that the end of the Epsig Log File indicates: "with EXIT_SUCCESS"
- Verifies that the command that was used for Epsig is correct. (Correct Epsig Binary used; Correct BINIMAGE Path used: i.e. G:\; Correct Datafiles referenced, i.e. MSL file is `self.MSLfile or self.nextMonth_MSLfile`; TSL file is `self.TSLfile`; PSL file is `self.PSLfile or nextMonth_PSLfile`

## `test_file_name_format.py`
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
