from util.structs import ClientInfo
from controllers.intefaces.model import ModelInterface
from ipaddress import ip_address, ip_network, IPv4Address, IPv4Network, \
    IPv6Network, IPv6Address
import re


class ModelController(object):

    def __init__(self, server):
        """ The underlying model from which we are querying information"""
        self._server: ModelInterface = server
        """ The current selected machine to display extended information"""
        self._current_machine = None
        """ The machines that are being displayed on the UI"""
        self._displayed_machines = set()
        """ The filter that determines the display machines"""
        self._filters = []
        """ The amount of times in seconds the controller will query info from the server """
        self._refresh_interval = 2

    # Backend Commands
    @property
    def current_machine(self):
        return self._current_machine

    def reset_current(self):
        self._current_machine = None

    def select_current(self, ip):
        if ip in self._server.get_hosts():
            self._current_machine = ip
        else:
            self._current_machine = None

    @property
    def displayed_machines(self):
        machine_info = []
        # add a filter to this to change it
        self._displayed_machines = self._server.get_hosts()
        for ip in self._displayed_machines:
            info = self.get_machine_info(ip)
            next_command = info.commands[0].command if info.commands else "N/A"
            tup = (info.beacon, info.hostname, info.ip, info.active, next_command)
            machine_info.append(tup)
        return machine_info

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, new_filter: dict):
        expected_values = {"ips", "hostname", "beacon", "active"}
        if  expected_values != set(new_filter.keys()):
            raise ValueError(f"modelcontoller.filter must contain values: {expected_values}")

        # TODO: do intelligent clearing. If a filter hasn't changed then dont clear it
        self._filters = []
        def ip_helper(ip, str):
            lst = str.strip().split(',')
            for x in lst:
                y = ip_network(x) if '/' in x else ip_address(x)
                if isinstance(y, IPv4Network) or isinstance(y, IPv6Network):
                    if ip_address(ip) in y:
                        return True
                if isinstance(y, IPv4Address) or isinstance(y, IPv6Address):
                    if ip_address(ip) == y:
                        return True

        if new_filter["ips"]:
            print("ips filter added")
            self._filters.append(lambda x: ip_helper(x, new_filter["ip"]))
        if new_filter["hostname"]:
            print("hostname filter added")
            self._filters.append(lambda x: re.compile(new_filter["hostname"]).match(x.hostname) is not None)
        if new_filter["beacon"]:
            print("beacon filter added")
            self._filters.append(lambda x: (x.beacon_type == new_filter["beacon"]) or new_filter["beacon"] is None)
        if new_filter["active"]:
            print("active filter added")
            self._filters.append(lambda x: x.active < int(new_filter["active"]))

    def _all_machine_info(self):
        machine_info = []
        # add a filter to this to change it
        self._displayed_machines = self._server.get_hosts()
        for ip in self._displayed_machines:
            info = self.get_machine_info(ip)
            next_command = info.commands[0].command if info.commands else "N/A"
            tup = (info.beacon, info.hostname, info.ip, info.active, next_command)
            machine_info.append(tup)
        return machine_info



    # ===========================================
    # Global Server Functions
    # ===========================================

    def backup(self):
        self._server.backup()

    def shutdown(self):
        self._server.shutdown()

    def get_hosts(self):
        """
        Get all the IP addresses that are currently being tracked
        :return: a list of IP addresses as strings
        """
        return self._server.get_hosts()

    def remove_host(self, ip):
        """
        Remove a host from the C2 Server. The server will no longer send
        commands to that host
        :param ip: the IP address
        :return: None
        """
        pass

    def add_host(self, ip, **kwargs):
        """
        Add a host to the C2 Server. The server will attempt to send commands
        to the host
        :param ip:
        :return: None
        """
        return self._server.add_host(ip, **kwargs)

    # ===========================================
    # Host Specific Commands
    # ===========================================

    def queue_command(self, ctype, ip, command):
        """
        Queue a single command on the given host
        :param ip: the IP of the host
        :param command: the powershell command to add
        :return: None
        """
        self._server.queue_command(ctype, ip, command)

    def remove_command(self, ip, cmd_id):
        """
        Remove a single command on the given host
        :param ip: the IP of the host
        :param cmd_id: the powershell command to remove
        :return: None
        """
        self._server.remove_command(ip, cmd_id)

    def get_queued_commands(self, ip):
        """
        Get the queued commands for a given IP address
        :param ip: the string IP address of the machine
        :return: a list of Command structs
        """
        return self._server.get_queued_commands(ip)

    def get_sent_commands(self, ip):
        return self._server.get_sent_commands(ip)

    def get_hostname(self, ip):
        """
        Get the hostname of a given IP address
        :param ip: the ip of the host
        :return: a string representing the hostname else N/A
        """
        info = self._server.get_machine_info(ip)
        if info.hostname:
            return info.hostname
        return "N/A"

    def get_last_active(self, ip):
        """
        Get the last known time the client beaconed out to Provenance
        :param ip: the ip of the host to check
        :return: a string in minutes
        """
        info = self._server.get_machine_info(ip)
        if info.active is not None:
            return f"{info.active}m"
        return "N/A"

    def get_machine_info(self, ip):
        info = self._server.get_machine_info(ip)
        # TODO: fix this janky stuff
        return ClientInfo(info.beacon, info.hostname, info.ip, self.get_last_active(ip), info.commands)


