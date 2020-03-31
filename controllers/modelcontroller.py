from frontend.util.structs import ClientInfo
from controllers.intefaces.model import ModelInterface


class ModelController(object):

    def __init__(self, server):
        self._server: ModelInterface = server
        self._current_machine = None

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

    # ===========================================
    # Global Server Functions
    # ===========================================

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
        if info.active:
            return info.active
        return "N/A"

    def get_machine_info(self, ip):
        return ClientInfo(*self._server.get_machine_info(ip))


