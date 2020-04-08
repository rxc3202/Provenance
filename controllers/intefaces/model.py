from abc import ABC, abstractmethod


class ModelInterface(ABC):

    # ===========================================
    # Global Server Functions
    # ===========================================

    @abstractmethod
    def shutdown(self):
        raise NotImplementedError("shutdown() must be implemented in concrete subclass")

    @abstractmethod
    def get_hosts(self):
        """
        Get all the IP addresses that are currently being tracked
        :return: a list of IP addresses as strings
        """
        raise NotImplementedError("get_hosts() must be implemented in concrete subclass")

    @abstractmethod
    def remove_host(self, ip):
        """
        Remove a host from the C2 Server. The server will no longer send
        commands to that host
        :param ip: the IP address
        :return: None
        """
        raise NotImplementedError("remove_host() must be implemented in concrete subclass")

    @abstractmethod
    def add_host(self, ip, **kwargs):
        """
        Add a host to the C2 Server. The server will attempt to send commands
        to the host
        :param ip:
        :return: None
        """
        raise NotImplementedError("add_host() must be implemented in concrete subclass")

    # ===========================================
    # Host Specific Commands
    # ===========================================

    @abstractmethod
    def queue_command(self, ctype, ip, command):
        """
        Queue a single command on the given host
        :param ip: the IP of the host
        :param command: the powershell command to add
        :return: None
        """
        raise NotImplementedError("queued_command() must be implemented in concrete subclass")

    @abstractmethod
    def remove_command(self, ip, cmd_id):
        """
        Remove a single command on the given host
        :param ip: the IP of the host
        :param command: the powershell command to remove
        :return: None
        """
        raise NotImplementedError("remove_command() must be implemented in concrete subclass")

    @abstractmethod
    def get_hostname(self, ip):
        """
        Get the hostname of a given IP address
        :param ip: the ip of the host
        :return: a string representing the hostname else N/A
        """
        raise NotImplementedError("get_hostname() must be implemented in concrete subclass")

    @abstractmethod
    def get_queued_commands(self, ip):
        """
        Get the queued commands for a given IP address
        :param ip: the string IP address of the machine
        :return: a list of Command structs
        """
        raise NotImplementedError("get_queued_commands() must be implemented in concrete subclass")

    @abstractmethod
    def get_sent_commands(self, ip):
        """
        Get the queued commands for a given IP address
        :param ip: the string IP address of the machine
        :return: a list of Command structs
        """
        raise NotImplementedError("get_sent_commands() must be implemented in concrete subclass")

    @abstractmethod
    def get_last_active(self, ip):
        """
        Get the last known time the client beaconed out to Provenance
        :param ip: the ip of the host to check
        :return: a string in minutes
        """
        raise NotImplementedError("get_last_active() must be implemented in concrete subclass")

    @abstractmethod
    def get_machine_info(self, ip):
        raise NotImplementedError("get_machine_info() must be implemented in concrete subclass")

    @abstractmethod
    def backup(self):
        """
        Backup the machine to a file using JSON-like format
        :return: None
        """
        raise NotImplementedError("backup() must be implemented in concrete subclass")


