import utils
from socketserver import UDPServer
import threading



class ProvenanceServer(UDPServer):
	
	def __init__(self, server_address, handler, args, bind_and_activate=True):
		super().__init__(server_address, handler, bind_and_activate)
		self.machines = {}
		self.whitelist = utils.parse_whitelist(args.whitelist)
		self.blacklist = []

	def get_request(self):
		return super().get_request()

	def verify_request(self, request, client_address):
		return super().verify_request(request, client_address)

	def process_request(self, request, client_address):
		addr, port = client_address
		print(f"Received from {addr}:{port}")
		if addr in self.machines.keys():
			self.machines[addr].request = request
			self.machines[addr].client_address = client_address
		else:
			self.machines[addr] = self.RequestHandlerClass(request, client_address, (addr, port))
		return self.finish_request(request, client_address)

	def finish_request(self, request, client_address):
		addr, port = client_address
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
		self.whitelist = utils.parse_whitelist(args.whitelist) if args.whitelist else []
		self.blacklist = []

	def process_request(self, request, client_address):
		# Create a unique handler for that machine if doesn't exist
		# Otherwise update the info needed to send packets
		addr, port = client_address
		if addr in self.machines.keys():
			self.machines[addr].request = request
			self.machines[addr].client_address = client_address
		else:
			self.machines[addr] = \
				self.RequestHandlerClass(request, client_address, (addr, port))

		thread = threading.Thread(target=self.finish_request,
								  args=(request, client_address))
		thread.daemon = self.daemon_threads

		# Shamelessly taken from socketserver.py
		if not thread.daemon and self.block_on_close:
			if self.threads is None:
				self.threads = []
			self.threads.append(thread)
		thread.start()

	def finish_request(self, request, client_address):
		addr, port = client_address
		return self.machines[addr].handle()

	def server_close(self):
		super().server_close()
		if self.block_on_close:
			_threads = self.threads
			self.threads = None
			if _threads:
				for t in _threads:
					t.join()
