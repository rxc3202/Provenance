class Controller(object):

    def __init__(self, server):
        self.server = server

    # Interactive commands
    def queue_command(self, ip, command):
        """
        Queue a single command on the given host
        :param ip: the IP of the host
        :param command: the powershell command to add
        :return: None
        """

    def remove_command(self, ip, command):
        """
        Remove a single command on the given host
        :param ip: the IP of the host
        :param command: the powershell command to remove
        :return: None
        """
        pass

    def remove_host(self, ip):
        """
        Remove a host from the C2 Server. The server will no longer send
        commands to that host
        :param ip: the IP address
        :return: None
        """
        pass

    def add_host(self, ip):
        """
        Add a host to the C2 Server. The server will attempt to send commands
        to the host
        :param ip:
        :return: None
        """
        pass

    # Query Commands
    def get_queued_commands(self, ip):
        return self.server.get_queued_commands(ip)

    def get_machine(self, ip):
        return self.server.get_machine(ip)


