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
import util.arguments as argopts
from controllers import *


def main():
    args = argopts.parse_arguments()
    socket = (args.interface, args.port)

    # Initialize Logging settings for Provenance, basically telling
    # the "Provenance" logger to redirect to the specified logfile AND
    # to the UI
    logger_controller = LoggingController(logfile="logs/provenance.log")
    logger = logging.getLogger("Provenance")

    # Initialize Backend
    try:
        if args.threading:
            server = ThreadedProvenanceServer(
                server_address=socket,
                handler=ProvenanceClientHandler,
                discovery=args.discovery,
                whitelist=args.whitelist,
                backup_dir="backups",
                restore=args.restore
            )
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
    logger.critical(f"Server starting on {socket[0]}:{socket[1]}.")

    # Initialize Frontend
    if args.ui == "cli":
        ProvenanceCLI.model = model_controller
        ProvenanceCLI.logger = logger_controller
        ProvenanceCLI.ui = ui_controller
        ProvenanceCLI.run()


if __name__ == '__main__':
    main()
