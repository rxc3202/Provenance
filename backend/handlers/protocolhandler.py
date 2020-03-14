from abc import ABC, abstractmethod
from enum import Enum


class Commands(Enum):
    """ The types of commands that can be on the victim

    * NOP = Do nothing
    * POWERSHELL = Run something in powershell
    * CMD = Run Something in cmd

    """
    NOP = 0
    POWERSHELL = 1
    CMD = 2


class ProtocolHandler(ABC):
    """
    An abstract class that defines the methods that need
    to be implemented so that Provenance can handle the
    request being received with the correct protocol.
    """

    @abstractmethod
    def handle_request(self, raw_request, port):
        """
        A required method that will take the raw request received by
        :module: socketserver.UDPServer, parse it and send back the response
        to the given port
        :param raw_request: the request found in :module: socketserver.UDPServer
        :param port: the port to send the response to
        :return: None
        """
        raise NotImplementedError("handle_request() not implemented in subclass.")

    @abstractmethod
    def queue_command(self, cmd_type, cmd):
        """    
        A required method that lets the server interface with the model to
        queue a command
        :param cmd_type: an enum constant from :module: protocolhandler.Commands
        :param cmd: the command to be run in the terminal
        :return: None
        """
        raise NotImplementedError("queue_command() not implemented in subclass.")

    @abstractmethod
    def send_command(self, request, port):
        """
        A required method that lets the server interface with the model to
        send a command
        :param request: the request received from :module: BaseRequestHandler
        :param port: the port that the client is receiving
        :return: None
        """
        raise NotImplementedError("send_command() not implemented in subclass.")

