#!/usr/bin/env python
from __future__ import print_function
import socket
from threading import Thread
import time
import ssl

def eprint(*args, **kwargs):
        import sys
        print(*args, file=sys.stderr, **kwargs)

# Todo List:
# 1. Make client response thread
# 2. Establish client encryption
#	See: https://stackoverflow.com/questions/26851034/opening-a-ssl-socket-connection-in-python
# 3. Handle unix kill signals gracefully
# 4. "log line" creation on local machine.

class clientInfo():
	def __init__(self, hostname, cpuinfo, cpucount, meminfo, disks, disksFree, accessTime):
		self.hostname = hostname
		self.cpuinfo = cpuinfo
		self.cpucount = cpucount
		self.meminfo = meminfo
		self.disks = disks
		self.disksFree = disksFree
		self.accessTime = accessTime

# makeLogLine - This function will obtain the data from the local machine, store it in a class,
# and parse that class into a json string. String returned to calling function.
# It should be easy for the client or any other applications to parse this Json. :)
def makeLogLine():
	import jsonpickle
	import psutil
	import datetime
	hostname   =	socket.getfqdn()
	cpuinfo    =	psutil.cpu_percent(interval=1)		# Get cpu info
	cpucount   =	psutil.cpu_count()
	meminfo    =	psutil.virtual_memory()			# Get RAM utilization
	disks      =	psutil.disk_partitions()		# Get disk free space info
	disksFree  =	(psutil.disk_usage(x.mountpoint) for x in disks)
	accessTime =	str(datetime.datetime.now())
	cliInf     =	clientInfo(hostname, cpuinfo, cpucount, meminfo, disks, disksFree, accessTime)
	mystr      =	jsonpickle.encode(cliInf)
	return mystr

# Handle one single client in a multithreaded fashion.
# Note that, unlike most servers, we don't have an infinite loop here.
# That's just because the server is tailored to the end goal of
# sending ONE singular string.
class clientThread(Thread):
	def __init__(self, conn, ip, port):
		Thread.__init__(self)
		self.conn = conn
		self.ip = ip
		self.port = port
		self.connected = False
	def run(self):
		self.connected = True
		self.conn.send(makeLogLine())
		self.conn.close()
		self.connected = False


def main():
	# Before we mess around with SSL, let's try to get a plaintext socket working.
	s = socket.socket()
	#host = socket.gethostname()
	port = 25560		# Hopefully, no one will mistake us for a Minecraft server.
	s.bind(('', port))
	threads = []
	try:
		while True:
			s.listen(1)
			conn, (ip, port) = s.accept()
			newthread = clientThread(conn, ip, port)
			newthread.start()
			threads.append(newthread)
			for t in threads:		# Basically, garbage collection. Kinda.
				if t.connected == False:
					threads.remove(t)
	except KeyboardInterrupt as e:
		eprint("Keyboard interrupt caught, shutting server down as gracefully as possible.")
	finally:
		for t in threads:
			t.join()
		s.close()

if __name__ == "__main__":
	main()
