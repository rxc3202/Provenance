from abc import ABC, abstractmethod
from enum import Enum
import logging
from util.structs import Command

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


class ProtocolHandler(ABC):
    """
    An abstract class that defines the methods that need
    to be implemented so that Provenance can handle the
    request being received with the correct protocol.
    """
    def __init__(self, ip, socket):
        self.logger = logging.getLogger("Provenance")
        self._ip = ip
        self._socket = socket

    @property
    def ip(self):
        return self._ip

    @property
    def socket(self):
        return self._socket

    @abstractmethod
    def handle_request(self, raw_request, port: int, cmd: Command):
        """
        A required method that will take the raw request received by
        :module: socketserver.UDPServer, parse it and send back the response
        to the given port
        :param raw_request: the request found in :module: socketserver.UDPServer
        :param port: the port to send the response to
        :param cmd: the command to send
        :return: None
        """
        raise NotImplementedError("handle_request() not implemented in subclass.")
