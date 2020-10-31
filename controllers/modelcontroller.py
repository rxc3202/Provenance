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
        self._displayed_machines = []
        """ The filter that determines the display machines"""
        self._filters = []
        """ The amount of times in seconds the controller will query info from the server """
        self._refresh_interval = 2

        for ip in self._server.get_hosts():
            m = self._server.get_machine(ip)
            self._displayed_machines.append(m)

    # Backend Commands
    @property
    def current_machine(self):
        """
        Get the ProvenanceClient instance that is currently selected in the UI
        :return: a ProvenanceClient instance
        """
        return self._current_machine

    def reset_current(self):
        """
        Reset the current value of _current_machine to None. Effectively saying
        that there is no currenlty selected machine in focus
        :return: None
        """
        self._current_machine = None

    def select_current(self, uuid: str):
        """
        Set the currently selected machine to the ip if it is being tracked
        by the server
        :param uuid: the uuid of the host
        :return:
        """
        if uuid in self._server.get_hosts():
            self._current_machine = uuid
        else:
            self._current_machine = None

    @property
    def displayed_machines(self):
        """
        Get the ClientInfo tuples of the machines that should be displayed
        by the UI
        :return: a list of tuples
        """
        self._update_hosts()
        displayed_info = []
        for m in self._displayed_machines:
            info = self.get_machine_info(m.uuid)
            next_command = info.commands[0].command if info.commands else "N/A"
            tup = (info.beacon, info.os, info.hostname, info.ip, info.active, next_command, info.uuid)
            displayed_info.append(tup)
        return displayed_info

    @property
    def filters(self):
        """
        Return the filter functions used to filter the hosts
        :return: a list of lambdas
        """
        return self._filters

    @filters.setter
    def filters(self, new_filter: dict):
        """
        Set a new filter for the hosts that will be given to the UI. The input
        is a dictionary containing the keys:
                ["ips", "hostname", "beacon", "active"]
        which filter on the attributes given in ProvenanceClient.

        Accepted Values:
            ips - is a string of CIDR IPs/subnets delimited by a comma
            hostname - a python3 valid regex
            beacon - a string representing the type of beacon to filter for
            active - a string of an int denoting that all beacons that have been
                     active within this amount of time are shown

        :param new_filter: a dictionary containing values
        :return: None
        """
        expected_values = {"ips", "hostname", "beacon", "active", "os"}
        if expected_values != set(new_filter.keys()):
            raise ValueError(f"modelcontoller.filter must contain values: {expected_values}")

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

        def active_helper(m, f):
            if m.active == "N/A":
                return False
            else:
                return int(m.active) <= int(f)

        # Generate the new filters
        self._filters = []
        if new_filter["ips"]:
            self._filters.append(lambda x: ip_helper(x.ip, new_filter["ips"]))
        if new_filter["hostname"]:
            self._filters.append(lambda x: re.compile(new_filter["hostname"]).search(x.hostname) is not None)
        if new_filter["beacon"]:
            self._filters.append(lambda x: (x.beacon == new_filter["beacon"]) or new_filter["beacon"] is None)
        if new_filter["active"]:
            self._filters.append(lambda x: active_helper(x, new_filter["active"]))
        if new_filter["os"]:
            self._filters.append(lambda x: (x.beacon == new_filter["os"]) or new_filter["os"] is None)

        self._update_hosts()

    def _update_hosts(self):
        # Apply the filters to the hosts that are being displayed
        new_displayed_machines = []
        for ip in self._server.get_hosts():
            info = self.get_machine_info(ip)
            # Only if the users has set new filters
            # Check if the machine passes all filters
            res = [f(info) for f in self._filters]
            if not all(res):
                continue
            # If there are no changes to the filters or the machine passed the test then add it
            m = self._server.get_machine(ip)
            new_displayed_machines.append(m)
        self._displayed_machines = new_displayed_machines

        # TODO: do intelligent clearing. If a filter hasn't changed then dont clear it

    # ===========================================
    # Global Server Functions
    # ===========================================

    def backup(self):
        """
        Tell the server to create a backup of itself to be restored latter
        :return: None
        """
        self._server.backup()

    def shutdown(self):
        """
        Shutdown the server using its shutdown method
        :return: None
        """
        self._server.shutdown()

    def get_hosts(self):
        """
        Get all the IP addresses that are currently being tracked
        :return: a list of IP addresses as strings
        """
        return self._server.get_hosts()

    def remove_host(self, uuid: str):
        """
        Remove a host from the C2 Server. The server will no longer send
        commands to that host
        :param uuid: the uuid identifying the host
        :return: None
        """
        pass

    def add_host(self, uuid: str, **kwargs):
        """
        Add a host to the C2 Server. The server will attempt to send commands
        to the host
        :param uuid: the uuid to track on the server
        :return: None
        """
        return self._server.add_host(uuid, **kwargs)

    # ===========================================
    # Host Specific Commands
    # ===========================================

    def queue_command(self, ctype: str, uuid: str, command: str):
        """
        Queue a single command on the given host
        :param ctype: a string of "ps", "bash", "cmd", or "nop"
        :param uuid: the uuid of the host
        :param command: the command to add
        :return: None
        """
        self._server.queue_command(ctype, uuid, command)

    def remove_command(self, uuid: str, cmd_id):
        """
        Remove a single command on the given host
        :param uuid: the uuid of the host
        :param cmd_id: the powershell command to remove
        :return: None
        """
        self._server.remove_command(uuid, cmd_id)

    def get_queued_commands(self, uuid: str) -> list:
        """
        Get the queued commands for a given IP address
        :param uuid: the uuid of the machine
        :return: a list of Command structs
        """
        return self._server.get_queued_commands(uuid)

    def get_sent_commands(self, uuid: str) -> list:
        """
        Get all the commands sent for the server
        :param uuid:
        :return:
        """
        return self._server.get_sent_commands(uuid)

    def get_hostname(self, uuid: str) -> str:
        """
        Get the hostname of a given IP address
        :param uuid: the uuid of the host
        :return: a string representing the hostname else N/A
        """
        info = self._server.get_hostname(uuid)
        if info:
            return info
        return "N/A"

    def get_last_active(self, uuid: str) -> str:
        """
        Get the last known time the client beaconed out to Provenance
        :param ip: the ip of the host to check
        :return: a string in minutes
        """
        info = self._server.get_last_active(uuid)
        if info is not None:
            return f"{info}m"
        return "N/A"

    def get_beacon_type(self, uuid: str) -> str:
        """
        Get the type of beacon the ip is using
        :param uuid: the uuid address as a string
        :return: a string of "DNS", "ICMP", "HTTP", etc
        """
        info = self._server.get_beacon(uuid)
        if info is not None:
            return info
        return "Not Set"

    def get_os(self, uuid: str) -> str:
        info = self._server.get_os(uuid)
        if info is not None:
            return info
        return "N/A"
    
    def get_ip(self, uuid: str) -> str:
        info = self._server.get_ip(uuid)
        return info

    def get_machine_info(self, uuid: str):
        """
        Return the information that the UI will be displaying wrapped up in a tuple
        :param ip: the IP of the machine to get the details for
        :return: a ClientInfo namedtuple
        """
        try:
            client = ClientInfo(
                self.get_beacon_type(uuid),
                self.get_os(uuid), self.get_hostname(uuid),
                self.get_ip(uuid),
                self.get_last_active(uuid),
                self.get_queued_commands(uuid),
                uuid)
            return client
        except Exception as e:
            self._server.logger.debug(str(e))
            return ClientInfo("BEACON", "OS", "HOST", "IP", "ACTIVE", [], "UUID")
