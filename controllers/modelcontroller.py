class Controller(object):

    def __init__(self, server):
        self.server = server

    # Interactive commands
    def queue_command(self, ctype, ip, command):
        """
        Queue a single command on the given host
        :param ip: the IP of the host
        :param command: the powershell command to add
        :return: None
        """
        self.server.queue_command(ctype, ip, command)

    def remove_command(self, ip, cmd_id):
        """
        Remove a single command on the given host
        :param ip: the IP of the host
        :param command: the powershell command to remove
        :return: None
        """
        self.server.remove_command(ip, cmd_id)

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
        self.server.add_host(ip)

    # Query Commands
    def get_queued_commands(self, ip):
        return self.server.get_queued_commands(ip)

    def get_hostname(self, ip):
        info = self.server.get_host_info(ip)
        return info[0]

    def get_num_queued_commands(self, ip):
        info = self.server.get_host_info(ip)
        return info[3]

    def get_last_active(self, ip):
        info = self.server.get_host_info(ip)
        return info[2]

    def get_machine_info(self, ip):
        return self.server.get_machine_info(ip)

    def get_hosts(self):
        return self.server.get_hosts()


