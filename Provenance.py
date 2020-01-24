"""
Filename:		Provenance.py
Author:			Ryan Cervantes
Description:	The main running file for the Provenance C2 
"""

from backend.server.requesthandler import IndividualClientHandler
from backend.server.ProvenanceServer import ProvenanceServer, ThreadedProvenanceServer
import sys
import threading
import time
import backend.util.arguments as parser


def main():
	global args
	args = parser.parse_arguments()
	# print(f"namespace: {args}")
	socket = (args.interface, args.port)
	try:
		print(f"[INFO] Server starting on {socket[0]}:{socket[1]}.")
		if args.threaded:
			server = ThreadedProvenanceServer(socket, IndividualClientHandler, args)
			# Start a thread with the server -- that thread will then start one
			# more thread for each request
			server_thread = threading.Thread(target=server.serve_forever)
			# Exit the server thread when the main thread terminates
			server_thread.daemon = True
			server_thread.start()
			print("Server is running on", server_thread.name)
			time.sleep(1000) # just for testing
		else:
			server = ProvenanceServer(socket, IndividualClientHandler, args)
			server.serve_forever()
	except KeyboardInterrupt:
		print("[INFO] Exiting.")
		sys.exit(0)


if __name__ == '__main__':
	main()
