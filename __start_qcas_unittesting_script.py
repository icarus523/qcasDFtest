import subprocess
import getpass
import glob
import os
import hashlib
import logging
import test_psl_file_content
import test_file_name_format
import test_datafiles
import test_chk01_intensive_checklist
import test_msl_file_content
import test_tsl_file_content
import test_chk01_checklist
import test_epsig_log_files
import test_chk01_checklist_game_removals
import unittest
import json

from datetime import datetime
from test_datafiles import Preferences, skipping_PSL_comparison_tests, QCASTestClient
from tkinter import messagebox
import tkinter as tk

# Configure Console Window
os.system('mode con: cols=150 lines=120')

# Configure logging to file and format
logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s - %(levelname)-8s %(message)s',
        datefmt='%d-%m-%y %H:%M',
        filename='qcas_test.log',
        filemode='a')
                
my_preferences = Preferences()
def_str = "==== QCAS Datafiles Testing started on: " + str(datetime.now()) + " by: " + getpass.getuser()  + " ===="
logging.getLogger().info(def_str)    

config = json.dumps(my_preferences.data, sort_keys=True, indent=4, separators=(',', ': '))
logging.getLogger().info("QCAS Datafiles Testing Configuration: \n" + config)

logging.getLogger().info("==== QCAS Datafiles Test script versions: ====")

unit_test_files = glob.glob("test*.py")
for file in unit_test_files:
    logging.getLogger().info("%35s\t%s" % (file, QCASTestClient.dohash_sha256(self=None, fname=file)))

logging.getLogger().info("==== Starting Unit Tests ====")

# Build Tests         
my_test_output = my_preferences.data['unittests'] # read from preference file
my_unittests = list()

# These have to match what's in preferences.dat
for test_output in my_test_output:    
    if test_output.strip() == "CHK01 Intensive validations":
        my_unittests.append(test_chk01_intensive_checklist)
    elif test_output.strip() == "CHK01 game removals":
        my_unittests.append(test_chk01_checklist_game_removals)                
    elif test_output.strip() == "Datafile Filename format tests":
        my_unittests.append(test_file_name_format)
    elif test_output.strip() == "MSL File Content Tests:":
        my_unittests.append(test_msl_file_content)
    elif test_output.strip() == "PSL File Content Tests:":
        my_unittests.append(test_psl_file_content)
    elif test_output.strip() == "TSL File Content Tests:":
        my_unittests.append(test_tsl_file_content)
    elif test_output.strip() == "epsig log file content tests":
        my_unittests.append(test_epsig_log_files)
    elif test_output.strip() == "CHK01 Validations":
        my_unittests.append(test_chk01_checklist)
       
# Run Tests
for test in my_unittests: 
    testLoad = unittest.TestLoader().loadTestsFromModule(test)      
    testResult = unittest.TextTestRunner(verbosity=3).run(testLoad) 

    for err in testResult.errors: 
        for err_detail in err: 
            logging.getLogger().error(err_detail) # log any errors as errors in full
    
    for skip in testResult.skipped: 
        #for skip_details in skip:
        logging.getLogger().warning(skip) # log any skipped tests as warnings
    
    for fail in testResult.failures: 
        for fail_details in fail: 
            logging.getLogger().error(fail_details) # log any test failures as errors in full
        
    logging.getLogger().debug(my_test_output[my_unittests.index(test)] + str(testResult)) # summary

display_msg = "QCAS Datafiles Validation COMPLETE: " + str(datetime.now()) + " by: " + getpass.getuser()
logging.getLogger().info("==== " + display_msg + " ====")

# GUI elements
root = tk.Tk()
root.withdraw() # hide window
messagebox.showinfo("Finished!", display_msg)
