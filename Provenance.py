"""
Filename:		Provenance.py
Author:			Ryan Cervantes
Description:	The main running file for the Provenance C2 
"""

import sys
import threading
import logging
from frontend.cli.clidriver import ProvenanceCLI
from backend.server.ProvenanceClient import ProvenanceClientHandler
from backend.server.ProvenanceServer import ProvenanceServer, ThreadedProvenanceServer
import backend.util.arguments as argopts
from controllers import *


def main():
	global args
	args = argopts.parse_arguments()
	socket = (args.interface, args.port)

	# Initialize Backend
	try:
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

	# Initialize Controllers for model-ui interactions
	ui_controller = UIController()
	model_controller = ModelController(server)
	logger_controller = LoggingController("logs/provenance.log")
	logger = logging.getLogger("Provenance")
	logger.critical(f"Server starting on {socket[0]}:{socket[1]}.")

	# Initialize Frontend
	if args.ui == "cli":
		ProvenanceCLI.model = model_controller
		ProvenanceCLI.logger = logger_controller
		ProvenanceCLI.ui = ui_controller
		frontend_thread = threading.Thread(target=ProvenanceCLI.run)
		frontend_thread.start()


if __name__ == '__main__':
	main()
