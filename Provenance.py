"""
Filename:		Provenance.py
Author:			Ryan Cervantes
Description:	The main running file for the Provenance C2 
"""

import sys
import threading
import time
import logging
from frontend.cli.clidriver import CLIDriver
from backend.server.requesthandler import IndividualClientHandler
from backend.server.ProvenanceServer import ProvenanceServer, ThreadedProvenanceServer
import backend.util.arguments as argopts

logger = logging.getLogger("Provenance")
logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(message)s")


def main():
	global args
	args = argopts.parse_arguments()
	logger.setLevel(argopts.verbosity(args.verbose))
	socket = (args.interface, args.port)

	if args.ui == "cli":
		cli = CLIDriver.generate()
		frontend_thread = threading.Thread(target=cli.run)
		frontend_thread.start()

	try:
		logger.critical(f"Server starting on {socket[0]}:{socket[1]}.")
		if args.threaded:
			server = ThreadedProvenanceServer(socket, IndividualClientHandler, args)
			# Start a thread with the server -- that thread will then start one
			# more thread for each request
			server_thread = threading.Thread(target=server.serve_forever)
			# Exit the server thread when the main thread terminates
			server_thread.daemon = True
			server_thread.start()
		else:
			server = ProvenanceServer(socket, IndividualClientHandler, args)
			server.serve_forever()
	except KeyboardInterrupt:
		sys.exit(0)


if __name__ == '__main__':
	main()
