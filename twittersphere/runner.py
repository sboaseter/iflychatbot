from subprocess import Popen
import psutil
for process in psutil.process_iter():
	try:
		if 'tstream.py' in process.cmdline():
			print('Process found. Terminating it.')
			process.terminate()
			break
	except:
		pass
else:
	print('Process not found: starting it.')
	Popen(['python', 'tstream.py'])
