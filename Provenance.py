"""
Filename:		Provenance.py
Author:			Ryan Cervantes
Description:	The main running file for the Provenance C2 
"""

import dnslib
from socketserver import UDPServer, BaseRequestHandler
import threading
from machine import IndividualClientHandler


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
												  (addr,port))

		return self.finish_request(request, client_address)

	def finish_request(self, request, client_address):
		addr, port = client_address
		return self.machines[addr].handle()

def main():
	socket = ("127.0.0.1", 53)	
	with ProvenanceServer(socket, IndividualClientHandler) as server:
		try:
			print(f"Starting Server on {socket[0]}:{socket[1]}...")
			server.serve_forever()
		except KeyboardException:
			pass
		finally:
			server.shutdown()



if __name__ == '__main__':
	main()
