"""
Filename:		Provenance.py
Author:			Ryan Cervantes
Description:	The main running file for the Provenance C2 
"""

import argparse
import sys
from ProvenanceServer import ProvenanceServer
from handler import IndividualClientHandler


def parse_arguments():
	parser = argparse.ArgumentParser(description="The Provenance C2 Server")
	# Positional Arguments
	parser.add_argument("ui",
					 choices=["gui", "cli"],
					 help="Run the server as a command line application or spawn a GUI")
	parser.add_argument("interface", help="The interface the C2 Sever is located on")
	parser.add_argument("port", type=int, default=53, help="The port on which the server listens")
	# Optional Arguments
	parser.add_argument("-v", "--verbose", action="count", help="""Use -v to display [INFO].
																   Use -vv to display [INFO] and [DEBUG].""")
	parser.add_argument("--discovery", action="store_true")
	parser.add_argument("--blacklist", nargs=1, help="Don't interact with these IPs")
	parser.add_argument("--whitelist", nargs=1, type=argparse.FileType('r'), default=sys.stdin, help="""Only interact with these IPs.
																			Use ':' to delimit IPs to hostnames (<ip>:<hostname>).
																			Takes precedence over blacklist. If no file is given,
																			then IPs will be read in from the commandline""")
	return parser.parse_args()


def main():
	global args
	args = parse_arguments()
	# print(f"namespace: {args}")
	socket = (args.interface, args.port)	
	with ProvenanceServer(socket, IndividualClientHandler, args) as server:
		try:
			print(f"Starting Server on {socket[0]}:{socket[1]}.")
			server.serve_forever()
		except KeyboardInterrupt:
			sys.exit(0)
		finally:
			server.shutdown()



if __name__ == '__main__':
	main()
