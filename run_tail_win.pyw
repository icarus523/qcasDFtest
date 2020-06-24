import subprocess
import os


# C:\\Users\\aceretjr\\Documents\\dev\\qcasDFtest\\
command = 'Get-Content -Path qcas_test.log -Wait -Tail 20'

proc = subprocess.Popen(['powershell.exe', command])
