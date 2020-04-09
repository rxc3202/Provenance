import logging
import threading
from socketserver import UDPServer
from util import parse_whitelist, get_whitelist, ip_in_list
from util.structs import ClientInfo
from controllers.intefaces.model import ModelInterface
import json
from datetime import datetime
import os.path
from backend.server.ProvenanceClient import ProvenanceClientHandler


class ProvenanceServer(UDPServer):
	"""
	An implementation :module: socketserver.UDPServer used
	to interact with various beacons. The methods defined
	in this class follow the specification on
	https://docs.python.org/3.7/library/socketserver.html
	"""

	def __init__(self, server_address, handler, bind_and_activate=True, discovery=True, whitelist=None, blacklist=None,
				 backup_dir="backups", restore=None):
		super().__init__(server_address, handler, bind_and_activate)
		self.logger = logging.getLogger("Provenance")
		self.machines = {}
		self.whitelist = []
		self.blacklist = []
		self.discovery = discovery
		self._backup_dir = backup_dir

		# Get the list of IPs we're supposed to interact with
		if not discovery:
			# via the whitelist argument
			if whitelist:
				hosts = parse_whitelist(whitelist)
			else:
				# or manually by command line (eww)
				hosts = get_whitelist()
			for h in hosts:
				self.add_host(ip=h[0], hostname=h[1], handler=h[2])

		if restore:
			self.logger.critical(f"Restoring backup from {restore[0]}")
			self.restore(restore[0])

	def get_request(self):
		return super().get_request()

	def verify_request(self, request, client_address):
		addr, _ = client_address

		# If we're not doing discovery, only whitelisted IPs are valid
		if not self.discovery:
			if ip_in_list(addr, self.whitelist):
				return super().verify_request(request, client_address)
			else:
				self.logger.info(f"{addr} not in whitelist.")
				return
		# Otherwise, we check if its in the whitelist
		# but blacklist takes precedence
		if ip_in_list(addr, self.whitelist):
			if ip_in_list(addr, self.blacklist):
				return
		return super().verify_request(request, client_address)

	def process_request(self, request, client_address):
		addr, port = client_address

		if addr in self.machines.keys():
			# Need to give handler the new request / new port
			self.machines[addr].update_handler(request, client_address)
		else:
			self.machines[addr] = self.RequestHandlerClass(
				request=request, client_address=client_address, serverinfo=self.server_address)
		return self.finish_request(request, client_address)

	def finish_request(self, request, client_address):
		addr = client_address[0]
		return self.machines[addr].handle()

	# TODO: add function typing for ModelController Methods
	def restore(self, file):
		try:
			with open(file, 'r') as file:
				data = json.load(file)
		except json.JSONDecodeError:
			self.logger.critical(f"Could not restore from {file}")
			return

		for machine_dict in data:
			ip = machine_dict["ip"]
			client: ProvenanceClientHandler = self.RequestHandlerClass(
				request=None, client_address=(ip, None), serverinfo=self.server_address
			)
			client.decode(machine_dict)
			self.machines[ip] = client

	def backup(self, fmt="%Y-%m-%d_%H~%M~%S", failover=True):
		# If there are no machines being tracked we don't care
		if not self.machines.keys():
			return

		def save_failure(d):
			if not failover:
				self.logger.critical(f"Backup failover is off. Backup not created.")
				return

			p = os.path.join(d, f"provenance_backup.bak")
			with open(p, "w") as out:
				json.dump(encodings, out)
			self.logger.critical(f"Creating safe backup file without errors: {p}")

		encodings = []
		for m in self.machines.values():
			encoding = m.encode()
			encodings.append(encoding)
		date = datetime.now().strftime(fmt)
		cwd = os.getcwd()
		filename = f"Provenance_{date}.bak"
		path = os.path.join(cwd, self._backup_dir, filename)
		if not os.path.exists(os.path.dirname(path)):
			os.makedirs(os.path.dirname(path))
		try:
			with open(path, "w") as file:
				json.dump(encodings, file)
			self.logger.critical(f"Backup saved to: {path}")
		except OSError as e:
			self.logger.error("Couldn't create backup file due OSError")
			self.logger.debug("Windows don't allow certain characters in filenames.")
			save_failure(cwd)

	def shutdown(self):
		pass

	# ===========================================
	# Model Interface Methods
	# ===========================================

	def get_hosts(self):
		return self.machines.keys()

	def add_host(self, ip, hostname=None, handler=None):
		new_handler = self.RequestHandlerClass(
			request=None, client_address=(ip, None), serverinfo=self.server_address,
			hostname=hostname, handler=handler or "DNS"
		)
		if ip not in self.machines.keys():
			self.machines[ip] = new_handler
			return True
		return False

	def get_machine_info(self, host):
		host = self.machines[host]
		return ClientInfo(host.beacon_type, host.get_hostname, host.get_ip, host.get_last_active, host.queued_commands)

	def get_queued_commands(self, host):
		machine = self.machines[host]
		return machine.get_queued_commands()

	def get_sent_commands(self, host):
		machine = self.machines[host]
		return machine.get_sent_commands()

	def queue_command(self, ctype, ip, cmd):
		machine = self.machines[ip]
		machine.queue_command(ctype, cmd)

	def remove_command(self, ip, cmd_id):
		machine = self.machines[ip]
		machine.remove_command(cmd_id)

	def remove_host(self, ip):
		pass

	def get_last_active(self, ip):
		machine = self.machines[ip]
		return machine.last_active

	def get_hostname(self, ip):
		machine = self.machines[ip]
		return machine.get_hostname()


class ThreadedProvenanceServer(ProvenanceServer, ModelInterface):
	""" A Threaded version of the Provenance server """

	# Decides how threads will act upon termination of the
	# main process
	daemon_threads = False
	# If true, server_close() waits until all non-daemonic threads terminate.
	block_on_close = True
	# For non-daemonic threads, list of threading.Threading objects
	# used by server_close() to wait for all threads completion.
	threads = []

	def __init__(self, server_address, handler, bind_and_activate=True, discovery=True,
				 whitelist=None, blacklist=None, backup_dir="backups", restore=None):
		super().__init__(server_address, handler, bind_and_activate,
						 discovery, whitelist, blacklist, backup_dir, restore)

	# Server Handling Methods
	def process_request(self, request, client_address):
		# Create a unique handler for that machine if doesn't exist
		# Otherwise update the info needed to send packets
		addr, port = client_address
		self.logger.debug(f"Processing request from: {addr}")
		if addr in self.machines.keys():
			self.machines[addr].update_handler(request, client_address)
		else:
			self.logger.info(f"New machine added: {addr}")
			self.machines[addr] = self.RequestHandlerClass(
				request=request, client_address=client_address, serverinfo=(addr, port))

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

	def shutdown(self):
		self.logger.critical(f"Server shutting down")
		super().server_close()
		if self.block_on_close:
			_threads = self.threads
			self.threads = None
			if _threads:
				for t in _threads:
					t.join()
