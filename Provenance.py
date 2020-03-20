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
from frontend.cli.menus.asciiMenu import ProvenanceCLI
from backend.server.ProvenanceClient import ProvenanceClientHandler
from backend.server.ProvenanceServer import ProvenanceServer, ThreadedProvenanceServer
import backend.util.arguments as argopts
from controllers.modelcontroller import Controller

logger = logging.getLogger("Provenance")
logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(message)s")


def main():
	global args
	args = argopts.parse_arguments()
	logger.setLevel(argopts.verbosity(args.verbose))
	socket = (args.interface, args.port)

	# Initialize Backend
	try:
		logger.critical(f"Server starting on {socket[0]}:{socket[1]}.")
		if args.threaded:
			server = ThreadedProvenanceServer(server_address=socket, handler=ProvenanceClientHandler, discovery=args.discovery)
			# Start a thread with the server -- that thread will then start one
			# more thread for each request
			server_thread = threading.Thread(target=server.serve_forever)
			# Exit the server thread when the main thread terminates
			server_thread.daemon = True
			server_thread.start()
		else:
			server = ProvenanceServer(socket, ProvenanceClientHandler, args)
			server.serve_forever()
	except KeyboardInterrupt:
		sys.exit(0)

	# Initialize Controller
	controller = Controller(server)

	# Initialize Frontend
	if args.ui == "cli":
		#cli = CLIDriver.generate(controller)
		#frontend_thread = threading.Thread(target=cli.run)
		ProvenanceCLI.model = controller
		frontend_thread = threading.Thread(target=ProvenanceCLI.run)
		frontend_thread.start()


if __name__ == '__main__':
	main()
