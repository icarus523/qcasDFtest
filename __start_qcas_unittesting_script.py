import subprocess
import getpass
import glob
import os
import hashlib
import logging

from datetime import datetime
from test_datafiles import Preferences, skipping_PSL_comparison_tests

os.system('mode con: cols=150 lines=2500')

# input: file to be hashed using sha256()
# output: hexdigest of input file    
def dohash_sha256(fname, chunksize=8192): 
    m = hashlib.sha256()         

    # Read in chunksize blocks at a time
    with open(fname, 'rb') as f:
        while True:
            block = f.read(chunksize)
            if not block: break
            m.update(block)    

    return m.hexdigest()

my_preferences = Preferences()
def_str = "\n ==== QCAS Unit Testing started on: " + str(datetime.now()) + " by: " + getpass.getuser()  + " ====\n"
print(def_str) 

print("\nUnit Test Configuration: ") 
if my_preferences.will_skip_lengthy_validations():
    print("\tSKIPPING LENGTHY VALIDATIONS!") 
    
if skipping_PSL_comparison_tests(): 
    print("\tONE MONTH VALIDATIONS!")
    
if my_preferences.verbose_mode.upper() == "TRUE":
    print("\tVERBOSE MODE = TRUE") 
else:
    print("\tVERBOSE MODE = FALSE") 


    

print("\nQCAS Unit Testing Configuration: " + my_preferences.toJSON() + "\n")

print("\n ==== QCAS Unit Test script versions: ==== \n")
unit_test_files = glob.glob("test*.py")
for file in unit_test_files:
    print("%30s\t%s" % (file, dohash_sha256(file)))
print("\n ==== Starting Unit Tests ====\n")
subprocess.call('py -m unittest', shell=False)
# pid = subprocess.Popen(args=['cmd.exe', '--command=py -m unittest']).pid
