import subprocess
import getpass
from datetime import datetime
from test_datafiles import Preferences

my_preferences = Preferences()

print("QCAS Unit Testing started on: " + str(datetime.now()) + " by: " + getpass.getuser())
print("QCAS Unit Testing Configuration: " + my_preferences.toJSON())


subprocess.call('py -m unittest -v', shell=True)
pid = subprocess.Popen(args=['cmd.exe', '--command=py -m unittest -v']).pid
