import subprocess

subprocess.call('py findgame.py -h', shell=True)
pid = subprocess.Popen(args=['cmd.exe', '--command=py findgame.py']).pid
