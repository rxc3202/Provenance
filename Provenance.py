"""
Filename:		Provenance.py
Author:			Ryan Cervantes
Description:	The main running file for the Provenance C2 
"""

import dnslib
from socketserver import UDPServer, BaseRequestHandler
import threading
from machine import Machine


class ProvenanceServer(UDPServer):
	
	def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
		super().__init__(server_address, RequestHandlerClass, bind_and_activate)
		self.machines = {}


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
												  (addr,port), "test")

		return self.finish_request(request, client_address)

	def finish_request(self, request, client_address):
		addr, port = client_address
		return self.machines[addr].handle()

def main():
	
	with ProvenanceServer(("localhost", 5555), Machine) as server:
		print("Starting Server...")
		server.serve_forever()



if __name__ == '__main__':
	main()
