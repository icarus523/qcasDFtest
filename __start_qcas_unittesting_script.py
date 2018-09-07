import subprocess
import getpass
import glob
import os
import hashlib
from datetime import datetime
from test_datafiles import Preferences, CHECK_ONE_FILE_ONLY_FLG

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
def_str = "\n ==== QCAS Unit Testing started on: " + str(datetime.now()) + " by: " + getpass.getuser()

if my_preferences.will_skip_lengthy_validations() and my_preferences.nextMonth_MSLfile == CHECK_ONE_FILE_ONLY_FLG:
    print(def_str + " SKIPPING LENGTHY VALIDATIONS! with One Month Only ====\n")
elif my_preferences.will_skip_lengthy_validations():
    print(def_str + " SKIPPING LENGTHY VALIDATIONS!")
else: 
    print(def_str + "\n")

print("\nQCAS Unit Testing Configuration: " + my_preferences.toJSON() + "\n")

print("\n ==== QCAS Unit Test script versions: ==== \n")
unit_test_files = glob.glob("test*.py")
for file in unit_test_files:
    print("%30s\t%s" % (file, dohash_sha256(file)))
print("\n ==== Starting Unit Tests ====\n")
subprocess.call('py -m unittest -v', shell=True)
pid = subprocess.Popen(args=['cmd.exe', '--command=py -m unittest -v']).pid
