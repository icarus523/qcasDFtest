# qcasDFtest
Unit Testing of QCAS datafiles

To use in Windows: `py -m unittest -v`
Will run all unit test scripts. To specify a specifc unit test use: `py -m unittest test_chk01_checklist.py`

## `test_datafiles.py`
Main class (QCASTestClient) derived from unittest.TestCase, includes the following helper class files: `PSLfile`, `MSLfile`, `TSLfile` and `CacheFile`. 

The QCASTestClient includes all modules that have common test procedures. 

## `test_chk01_checklist.py`
Mirrors the checks specified in CHK01 Casino Datafiles checklist, the following unit tests are performed in this test: 

#### `test_Generated_PSL_files_Differ()`
This unit test will check that the two PSL files: `self.PSLfile and self.nextMonth_PSLfile` refer to `test_datafiles.py:setUp()` module referenced in the script are not the same. 

#### `test_new_games_to_be_added_are_in_PSL_files()`
