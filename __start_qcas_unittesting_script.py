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

# Configure Console Window
os.system('mode con: cols=150 lines=120')

# Configure logging to file and format
logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s - %(levelname)-8s %(message)s',
        datefmt='%d-%m-%y %H:%M',
        filename='qcas_test.log',
        filemode='a')
                
my_preferences = Preferences()
def_str = "==== QCAS Unit Testing started on: " + str(datetime.now()) + " by: " + getpass.getuser()  + " ===="
logging.getLogger().info(def_str)    

config = json.dumps(my_preferences.data, sort_keys=True, indent=4, separators=(',', ': '))
logging.getLogger().info("QCAS Unit Testing Configuration: \n" + config)

logging.getLogger().info("==== QCAS Unit Test script versions: ====")

unit_test_files = glob.glob("test*.py")
for file in unit_test_files:
    logging.getLogger().info("%35s\t%s" % (file, QCASTestClient.dohash_sha256(None,file)))

logging.getLogger().info("==== Starting Unit Tests ====")
# subprocess.call('py -m unittest', shell=False)

# Build Tests         
my_unittests = list() # clear list    
my_test_output = list() # clear list

my_unittests.append(test_chk01_intensive_checklist)
my_test_output.append("CHK01 intensive validations")          

my_unittests.append(test_chk01_checklist_game_removals)
my_test_output.append("CHK01 game removals")   

my_unittests.append(test_file_name_format)
my_test_output.append("Datafile filename format tests")

my_unittests.append(test_msl_file_content)
my_test_output.append("MSL file content Tests: ")

my_unittests.append(test_psl_file_content)
my_test_output.append("PSL file content Tests: ")

my_unittests.append(test_tsl_file_content)
my_test_output.append("TSL file content tests: ")        

my_unittests.append(test_epsig_log_files)
my_test_output.append("epsig log file content tests: ")   

my_unittests.append(test_chk01_checklist)
my_test_output.append("CHK01 validations: ")          

# Run Tests
for test in my_unittests: 
    testLoad = unittest.TestLoader().loadTestsFromModule(test)      
    testResult = unittest.TextTestRunner(verbosity=3).run(testLoad) 

    for err in testResult.errors: 
        for err_detail in err: 
            logging.getLogger().error(err_detail) # log any errors as errors in full
    
    for skip in testResult.skipped: 
        for skip_details in skip:
            logging.getLogger().warning(skip_details) # log any skipped tests as warnings
    
    for fail in testResult.failures: 
        for fail_details in fail: 
            logging.getLogger().error(fail_details) # log any test failures as errors in full
        
    logging.getLogger().debug(my_test_output[my_unittests.index(test)] + str(testResult)) # summary

display_msg = "QCAS Datafiles Validation COMPLETE: " + str(datetime.now()) + " by: " + getpass.getuser()
logging.getLogger().info("==== " + display_msg + " ====")
messagebox.showinfo("Finished!", display_msg)