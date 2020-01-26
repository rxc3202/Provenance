import logging
import threading
from socketserver import UDPServer
from backend.util.arguments import parse_ips, ip_in_list


class ProvenanceServer(UDPServer):
	"""
	An implementation :module: socketserver.UDPServer used
	to interact with various beacons. The methods defined
	in this class follow the specification on
	https://docs.python.org/3.7/library/socketserver.html
	"""
	
	def __init__(self, server_address, handler, args, bind_and_activate=True):
		super().__init__(server_address, handler, bind_and_activate)
		self.logger = logging.getLogger("Provenance")
		self.machines = {}
		self.whitelist = [] or parse_ips(args.whitelist)
		self.blacklist = [] or parse_ips(args.blacklist)

	def get_request(self):
		return super().get_request()

	def verify_request(self, request, client_address):
		addr, _ = client_address
		if self.whitelist:
			if ip_in_list(addr, self.whitelist):
				self.logger.info(f"{addr} not in whitelist.")
				return
			else:
				if ip_in_list(addr, self.blacklist):
					return
		else:
			if self.blacklist:
				if addr in self.blacklist:
					return
		return super().verify_request(request, client_address)

	def process_request(self, request, client_address):
		addr, port = client_address

		if addr in self.machines.keys():
			# Need to give handler the new request / new port
			self.machines[addr].update_handler(request, client_address)
		else:
			self.machines[addr] = self.RequestHandlerClass(
				request, client_address, (addr, port))
		return self.finish_request(request, client_address)

	def finish_request(self, request, client_address):
		addr = client_address[0]
		return self.machines[addr].handle()


class ThreadedProvenanceServer(ProvenanceServer):
	""" A Threaded version of the Provenance server """

	# Decides how threads will act upon termination of the
	# main process
	daemon_threads = False
	# If true, server_close() waits until all non-daemonic threads terminate.
	block_on_close = True
	# For non-daemonic threads, list of threading.Threading objects
	# used by server_close() to wait for all threads completion.
	threads = []

	def __init__(self, server_address, handler, args, bind_and_activate=True):
		super().__init__(server_address, handler, args, bind_and_activate)
		self.machines = {}
		self.whitelist = []
		self.blacklist = []

	def process_request(self, request, client_address):
		# Create a unique handler for that machine if doesn't exist
		# Otherwise update the info needed to send packets
		addr, port = client_address
		if addr in self.machines.keys():
			self.machines[addr].update_handler(request, client_address)
		else:
			self.machines[addr] = self.RequestHandlerClass(
				request, client_address, (addr, port))

		thread = threading.Thread(
			target=self.finish_request,
			args=(request, client_address))
		thread.daemon = self.daemon_threads

		# Shamelessly taken from socketserver.py
		if not thread.daemon and self.block_on_close:
			if self.threads is None:
				self.threads = []
			self.threads.append(thread)
		thread.start()

	def finish_request(self, request, client_address):
		addr = client_address[0]
		return self.machines[addr].handle()

	def server_close(self):
		super().server_close()
		if self.block_on_close:
			_threads = self.threads
			self.threads = None
			if _threads:
				for t in _threads:
					t.join()
