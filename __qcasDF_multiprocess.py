import subprocess
import sys

procs = list() 
for i in range(1, 10): 
    proc = subprocess.Popen(['py.exe', '__start_qcas_unittesting_script.py'])
    procs.append(proc)
    
for proc in procs: 
    proc.wait() 
