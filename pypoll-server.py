#!/usr/bin/env python
import socket
from threading import Thread
import time
import ssl

# Todo List:
# 1. Make client response thread
# 2. Establish client encryption
#	See: https://stackoverflow.com/questions/26851034/opening-a-ssl-socket-connection-in-python
# 3. Handle unix kill signals gracefully
# 4. "log line" creation on local machine.

class clientInfo():
	def __init__(self):
		self.disks = []
		self.loadAvg = ""
		self.hostname = ""
		self.accessTime = ""

# makeLogLine - This function will obtain the data from the local machine, store it in a class,
# and parse that class into a json string. String returned to calling function.
# It should be easy for the client or any other applications to parse this Json. :)
def makeLogLine():
	import json
	cliInf = clientInfo
	# Get cpu info
	# Get RAM utilization
	# Get disk free space info
	return "Just testing for now."

class clientThread(Thread):
	def __init__(self, conn, ip, port):
		Thread.__init__(self)
		self.conn = conn
		self.ip = ip
		self.port = port
		self.connected = False
		#print("[+] New thread started for {}:{}".format(ip, port))
	def run(self):
		self.connected = True
		while True:
			print("sending")
			self.conn.send(makeLogLine())
			data = self.conn.recv(2048)
			print("sent")
			if not data: break
		#print("Client thread reached break statement.")
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
			for t in threads:		# Basically, garbage collection
				if t.connected == False:
					threads.remove(t)
	except KeyboardInterrupt as e:
		print("Keyboard interrupt caught, shutting server down as gracefully as possible.")
	finally:
		for t in threads:
			t.join()

if __name__ == "__main__":
	main()
