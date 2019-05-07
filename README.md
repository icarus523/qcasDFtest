# qcasDFtest
Unit Test scripts written in Python for validation of Queensland Casino datafiles. 

Rationale: CHK01 is essentially a manual process to verify an automated procedure for generating the Casino datafiles. The current procedure involves completing CHK01 Casino Datafiles Checklist which indicates that two officers have reviewed the datafiles generated are complete and error free. This process is laborious and time consuming however it can be automated to reduce the risk of officers not correctly following processes and provide consitency for this process. 

This script attempts to complete all CHK01 process as well as thoroughly check the outgoing Casino Datafiles for formating, naming convention and sanity checking. 

### [NEW] There is now a GUI to control the validation of casino datafiles. 
To use: 
1. Double-Click on `__qcasDF_gui_control.py`

2. Select Your Options from GUI 
3. Press [Start Verification]

### Manual Process
1. Modify preferences.dat file and change the following references: 

 ```
        "previous_TSLfile" : "qcas_2017_09_v02.tsl"
        "TSLfile" : "qcas_2017_10_v01.tsl"
        "PSLfile" : "qcas_2017_10_v03.psl"
        "nextMonth_PSLfile" : "qcas_2017_11_v01.psl"
        "MSLfile" :  "qcas_2017_10_v01.msl"
        "nextMonth_MSLfile" : "qcas_2017_11_v01.msl"
        
        "path_to_binimage" : "\\\\Justice.qld.gov.au\\Data\\OLGR-TECHSERV\\BINIMAGE"
        "epsig_log_file": "\\\\Justice.qld.gov.au\\Data\\OLGR-TECHSERV\\OLGR-TECHSERV\\MISC\\BINIMAGE\\qcas\\log\\epsig.log"  
        
        "previousMonth_PSLfile": "G:/OLGR-TECHSERV/MISC/BINIMAGE/qcas/qcas_2018_11_v03.psl",
        "previous_TSLfile": "G:/OLGR-TECHSERV/MISC/BINIMAGE/qcas/qcas_2018_11_v01.tsl",
```

#### Important Options
`previousMonth_PSLfile` is used to determine whether new games being included matches with what is being expected through: `TSLfile`.


2. On the command prompt (in Windows) use: `py -m unittest -v`
Will run all unit test scripts. To specify a specifc unit test use: `py -m unittest test_chk01_checklist.py`

Otherwise you can use the helper script named: `__start_qcas_unittesting_script.py`

3. Skipping tests
There is an option in the preferences.dat file to skip lengthy checks. 

```
    "skip_lengthy_validations": "FALSE"
```

Change the above variable to `"skip_lengthy_validations": "TRUE"` and the script will avoid any lengthy tests. These include: 
```
`test_new_games_to_be_added_are_in_PSL_files()`
`test_One_old_game_to_be_added_in_PSL_files_full()`
`test_One_new_game_to_be_added_in_PSL_files_full()`
`test_TSL_entries_exist_in_PSL_files()`
```
4. Test only a single month
There is now an option to test a single month: MSL, PSL files, set the following: 

```
    "one_month_mode": "TRUE",
```

Note: Previous month TSL is still mandatory, for testing single month datafiles 

5. Other configurations
Refer to `preferences.dat` file and change the following to suit

```
"percent_changed_acceptable" : 0.10,
```
This parameter is related to the PSL change in file size, i.e. 10% expected file size will be acceptable. 

```
"verbose_mode" : "false"
```
This parameter will display more "output" onscreen, including the generation of hashes for each component in a BLNK file. 
Can slow the script down. 

---
# Unit Test Module Details
## Module: `test_datafiles.py`
Main class (QCASTestClient) derived from unittest.TestCase. The QCASTestClient includes all modules that have common test procedures, it includes the following helper class files: `PSLfile`, `MSLfile`, `TSLfile`. 

#### Class Helper Files: MSLfile
Reads the text file and creates an Object, it also performs the following sanity checks: 
- verify year field is 2017 to 9999
- verify months fields is 1 to 12
- verify 31 seeds in file
- verify each seed is 8 characters long. 

#### Class Helper Files: PSLfile
- verify year field is 2017 to 9999 (and that it is only 4 characters)
- verify months fields is 1 to 12 (and that it is only 2 characters) 
- verify game name is less than 31 characters
- verify MID field is valid
- verify SSAN is only 10 characters
- verify that there is 31 hashes in for each PSL entry

#### Class Helper Files: TSLfile
- verify MID field is valid
- verify SSAN is only 10 characters
- verify game name is less than 61 characters
- verify BIN filename is less than 21 characters
- verify BIN Type is a valid type: Only "BLNK","PS32","SHA1" can be processed. 


## CHK01: Datafiles Checklist Module: `test_chk01_checklist.py`
Mirrors the checks specified in CHK01 Casino Datafiles checklist, the following unit tests are performed in this test: 

#### `test_PSL_files_are_Different()`
- Verifies that the two PSL files: `self.PSLfile and self.nextMonth_PSLfile` are not the same. 

#### `test_new_games_to_be_added_are_in_PSL_files()`
- Verifies if the SSANs of new games exist in both `self.PSLfile and self.nextMonth_PSLfile` files. 

#### `test_X_OLD_games_with_one_seed_in_PSL_file()`
- Similar to `test_One_old_game_to_be_added_in_PSL_files()` but utilises one random seed for both months for X number of games

#### `test_X_NEW_game_with_one_seed_in_PSL_file()`
- Similar to `test_One_new_game_to_be_added_in_PSL_files()` but utilises one random seed for both months for X number of games

## CHK01: Game Removal Module: `test_chk01_checklist_game_removals.py`

#### `test_Games_removed_from_PSL_files()`
- Verifies that expected games removed has been identified from the PSL files. 

## CHK01: Intensive Checklist Module: `test_chk01_intensive_checklist.py`

#### `test_TSL_entries_exist_in_PSL_files()`
Verifies the following entry for each new game generated: 
- Game Name is less than 30 characters long
- Manufacturer ID is valid: 00, 01, 05, 07, 09, 12, 17
- PSL Year field is valid: 2017 < year < 9999
- PSL Month field is valid:  1 < valid month < 12
- PSL SSAN is valid: 150000 < SSAN < 999999999
- Number of Hashes in the PSL entry is equal to 31

#### `test_One_new_game_to_be_added_in_PSL_files_full()`
- Verifies that the generated PSL entries for two months is created for the Random game. 
- Verifies that the PSL entries matches for two months exists in `self.PSLfile and self.nextMonth_PSLfile`

#### `test_One_old_game_to_be_added_in_PSL_files_full()`
- Verifies that the generated PSL entries for two months is created for the Random game. 
- Verifies that the PSL entries matches for two months exists in `self.PSLfile and self.nextMonth_PSLfile`

## Epsig Log file Verification Module: `test_epsig_log_files.py`
This test script verifies the expected output of the EPSIG log. 

#### `test_Read_Epsig_log_file_from_disk()`
- Verifies `self.my_preferences.data['epsig_log_file']` can be read from disk

#### `test_epsig_log_file_last_four_entries_are_valid_for_psl_versions()`
- Verifies the last four paragraphs in the epsig log file are complete and as expected. 
- Verifies that the end of each paragraph indicates: "with EXIT_SUCCESS"
- Verifies that the time stamp for when EPSIG last ran is reasonable (within 30 days)
- Verifies that the time stamp for when EPSIG last completed is reasonable (within 30 days)

#### `test_epsig_log_file_last_two_entries_command_str_is_valid()`
- Verifies the last entry of the Epsig log file
- Verifies the version of EPSIG being used (expected: v3.5)
- Verifies that the time stamp for when EPSIG last ran is reasonable (within 30 days)
- Verifies that the time stamp for when EPSIG last completed is reasonable (within 30 days)
- Verifies that the end of the Epsig Log File indicates: "with EXIT_SUCCESS"
- Verifies that the command that was used for Epsig is correct. (Correct Epsig Binary used; Correct BINIMAGE Path used: i.e. G:\; Correct Datafiles referenced, i.e. MSL file is `self.MSLfile or self.my_preferences.data['nextMonth_MSLfile']`; TSL file is `self.TSLfile`; PSL file is `self.PSLfile or self.nextMonth_PSLfile`
- Verifies that the PSL versions per month are incremented by 1. 

## Filename Test Module: `test_file_name_format.py`
Generic test scripts for correct file name format and conventions. 

#### `test_MSL_filename_ends_with_MSL()`
- Verifies that `MSLfile or nextMonth_MSLfile` ends with .msl

#### `test_MSL_filename_date()`
- Verifies that the month fields in `MSLfile or nextMonth_MSLfile` are not equal
- Verifies that the MSL filename month fields are not equal
- Verifies that the MSL year fields is the same if month is less than 12, otherwise an increment in Year value is expected

#### `test_MSL_filename_version()`
- Verifies that the MSL version fields must always be `v1`

#### `test_TSLfile_ends_with_TSL()`
- Verifies that the `self.TSLfile` file ends with '.tsl'

#### `test_PSLfile_ends_with_PSL()`
- Verifies that the `self.PSLfile or self.nextMonth_PSLfile` ends with '.psl'

#### `test_PSL_file_version_increment()`
- Verifies that the PSL file version should be incremented if not a new moth.

#### `test_PSL_filename_date()`
- Verify that current PSL month is not equal to the new PSL month 
- Verify that the PSL year is the same, unless current PSL month is December.
- Verify that if PSL month is new year then the Year field should be current month field + 1

## TSL file Module: `test_tsl_file_content.py`

####`test_Read_TSL_file_from_disk()`
- Verifies that `self.TSLfile` and `self.previous_TSLfile` can be read from disk

#### `test_TSL_content_can_be_parsed()`
- Verifies TSL file manufacturer field entries is valid
- Verifies TSL file SSAN field is unique
- Verifies TSL file Bin Image Type is valid 
- Verifies BNK file name is uniqe (Note, this fails and is disabled by default as BNK file: 0101230 duplicates exist. 

## PSL file Module: `test_psl_file_content.py`

##### `test_psl_size_is_reasonable()`
- Verifies that the file size of the PSL files is reasonable (greater than 1055KB as at July 2013)

#### `test_PSL_content_can_be_parsed()`
- Verifies the `self.PSLfile` and `self.nextMonth_PSLfile` file formats
- Verifies PSL file manufacturer field is valid
- Verifies PSL Game name field length is 30 characters or less
- Verifies PSL year field is this year's or next
- Verifies PSL month field is this month's or next
- Verifies that the PSL file has the same number of lines as the generated PSL entry

#### `test_Read_PSL_file_from_disk()`
- Verifies that `self.PSLfile` and `self.previous_PSLfile` can be read from disk

#### `test_valid_MIDs_have_PSL_entries()`
- Verifies that each Manufacturer has a PSL entry, on each PSL file

#### `test_date_field_in_PSL_entry_equals_date_field_in_filename()`
- Verifies that the date in the first PSL entry has the correct month & year, for both PSL files. 

## MSL file Module: `test_msl_file_content.py`
#### `test_MSL_size_is_reasonable()`
- Verifies that the file size of the MSL files is reasonable (The size should not change and is 1KB)

#### `test_MSL_content_can_be_parsed()`
- Verifies the `self.MSLfile` and `self.my_preferences.data['nextMonth_MSLfile']` file contents by reading parsing the files
- Verifies that the MSL object generated from the files only has one entry

#### `test_MSL_file_one_row()`
- Verifies that the MSL files only has one entry

#### `test_Read_MSL_file()`
- Verifies that the `self.MSLfile` and `self.my_preferences.data['nextMonth_MSLfile']` can be read from disk 

#### `test_MSL_fields_sanity_checks()`
- Performs sanity checks on MSL fields, for both MSL files
- Check Month Field to be either this month's or next month's, for both MSL files
- Check Year Field to be either this month's or next month's, for both MSL files
- Check number of Seeds equal 31, for both MSL files
