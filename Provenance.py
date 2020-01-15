"""
Filename:		Provenance.py
Author:			Ryan Cervantes
Description:	The main running file for the Provenance C2 
"""

import argparse
import dnslib
import threading
import utils
import sys
from socketserver import UDPServer, BaseRequestHandler
from machine import IndividualClientHandler


class ProvenanceServer(UDPServer):
	
	def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
		super().__init__(server_address, RequestHandlerClass, bind_and_activate)
		self.machines = {}
		self.whitelist = utils.parse_whitelist(args.whitelist)
		print(self.whitelist)
		self.blacklist = []


	def get_request(self):
		return super().get_request()

	def verify_request(self, request, client_address):
		return super().verify_request(request, client_address)

	def process_request(self, request, client_address):
		# TODO: spawn a new thread to handle this request and delegate 
		# to the correct machine
		addr, port = client_address
		if addr in self.machines.keys():
			self.machines[addr].request = request
		else:
			self.machines[addr] = self.RequestHandlerClass(request,
												  client_address,
												  (addr,port))

		return self.finish_request(request, client_address)

	def finish_request(self, request, client_address):
		addr, port = client_address
		return self.machines[addr].handle()


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
	print(f"namespace: {args}")
	socket = (args.interface, args.port)	
	with ProvenanceServer(socket, IndividualClientHandler) as server:
		try:
			print(f"Starting Server on {socket[0]}:{socket[1]}...")
			server.serve_forever()
		except KeyboardInterrupt:
			sys.exit(0)
		finally:
			server.shutdown()



if __name__ == '__main__':
	main()
