from abc import ABC, abstractmethod


class ModelInterface(ABC):

    # ===========================================
    # Global Server Functions
    # ===========================================

    @abstractmethod
    def shutdown(self):
        raise NotImplementedError("shutdown() must be implemented in concrete subclass")

    @abstractmethod
    def backup(self):
        """
        Backup the machine to a file using JSON-like format
        :return: None
        """
        raise NotImplementedError("backup() must be implemented in concrete subclass")

    @abstractmethod
    def restore(self, file):
        """
        Backup the machine to a file using JSON-like format
        :param file: the filename holding the JSON backup info created by backup()
        :return: None
        """
        raise NotImplementedError("restore() must be implemented in concrete subclass")

    # ===========================================
    # Interaction Server Functions
    # ===========================================

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
    def queue_command(self, ctype: str, uuid: str, command: str):
        """
        Queue a single command on the given host
        :param ctype: the type of the command as a string
        :param uuid: the uuid of the host
        :param command: the powershell command to add
        :return: None
        """
        raise NotImplementedError("queued_command() must be implemented in Model's concrete subclass")

    @abstractmethod
    def remove_command(self, uuid: str, cmd_id):
        """
        Remove a single command on the given host
        :param uuid: the uuid of the host
        :param command: the powershell command to remove
        :return: None
        """
        raise NotImplementedError("remove_command() must be implemented in Model's concrete subclass")

    @abstractmethod
    def get_hostname(self, uuid: str) -> str:
        """
        Get the hostname of a given IP address
        :param uuid: the uuid of the host
        :return: a string representing the hostname else N/A
        """
        raise NotImplementedError("get_hostname() must be implemented in Model's concrete subclass")

    @abstractmethod
    def get_queued_commands(self, uuid: str) -> str:
        """
        Get the queued commands for a given IP address
        :param uuid: the uuid of the host
        :return: a list of Command structs
        """
        raise NotImplementedError("get_queued_commands() must be implemented in Model's concrete subclass")

    @abstractmethod
    def get_sent_commands(self, uuid: str) -> str:
        """
        Get the queued commands for a given IP address
        :param uuid: the uuid of the host
        :return: a list of Command structs
        """
        raise NotImplementedError("get_sent_commands() must be implemented in Model's concrete subclass")

    @abstractmethod
    def get_last_active(self, uuid: str) -> str:
        """
        Get the last known time the client beaconed out to Provenance
        :param uuid: the uuid of the host
        :return: a string in minutes
        """
        raise NotImplementedError("get_last_active() must be implemented in Model's concrete subclass")

    @abstractmethod
    def get_beacon(self, uuid: str) -> str:
        """
        Get the type of beacon being used by the host
        :param uuid: the uuid of the host
        :return: a string representing the beacon type
        """
        raise NotImplementedError("get_beacon() must be implemented in Model's concrete subclass")

    @abstractmethod
    def get_os(self, uuid: str) -> str:
        """
        Get the os of the machine in question
        :param uuid: the uuid of the host
        :return: a string reprsenting the OS
        """
        raise NotImplementedError("get_beacon() must be implemented Model's in concrete subclass")

    @abstractmethod
    def get_machine(self, uuid: str) -> str:
        """
        Get the actual Provenance client instance
        :param uuid: the uuid of the host
        :return:
        """
        raise NotImplementedError("get_machine() must be implemented Model's in concrete subclass")

    @abstractmethod
    def get_ip(self, uuid: str) -> str:
        """
        Get the actual Provenance client instance
        :param uuid: the uuid of the host
        :return:
        """
        raise NotImplementedError("get_ip() must be implemented in Model's concrete subclass")

    @abstractmethod
    def get_state(self, uuid: str) -> str:
        """
        Get the actual Provenance client instance
        :param uuid: the uuid of the host
        :return: the current state of the client as kept internally by the server
        """
        raise NotImplementedError("get_ip() must be implemented in Model's concrete subclass")