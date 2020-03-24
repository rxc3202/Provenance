from frontend.util.structs import ClientInfo


class Controller(object):

    def __init__(self, server):
        self._server = server
        self._current_machine = None

    # Backend Commands
    def shutdown(self):
        self._server.server_close()

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

    # Interactive commands
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
        :param command: the powershell command to remove
        :return: None
        """
        self._server.remove_command(ip, cmd_id)

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

    # Query Commands
    def get_queued_commands(self, ip):
        return self._server.get_queued_commands(ip)

    def get_hostname(self, ip):
        info = self._server.get_host_info(ip)
        return info.hostname

    def get_last_active(self, ip):
        info = self._server.get_host_info(ip)
        return info.active

    def get_machine_info(self, ip):
        return ClientInfo(*self._server.get_machine_info(ip))

    def get_hosts(self):
        return self._server.get_hosts()


