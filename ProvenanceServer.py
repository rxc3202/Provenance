import dnslib
import threading
import utils
import sys
from socketserver import UDPServer, BaseRequestHandler
from handler import IndividualClientHandler


class ProvenanceServer(UDPServer):
	
	def __init__(self, server_address, RequestHandlerClass, args, bind_and_activate=True):
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
