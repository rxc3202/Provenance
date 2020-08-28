from abc import ABC, abstractmethod
from enum import Enum
import logging
from util.structs import Command
from socket import socket


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
        self._synchronized = False

    @property
    def ip(self):
        return self._ip

    @property
    def socket(self):
        return self._socket
    
    @socket.setter
    def socket(self, sock: socket):
        self._socket = sock

    @property
    def synchronized(self):
        return self._synchronized
    
    @synchronized.setter
    def synchronized(self, value: bool):
        self._synchronized = value

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

    @abstractmethod
    def synchronize(self, raw_request, port: int) -> (str,str):
        """
        A method that handles the initial synchronization between Provenance and
        the beacon to establish OS and hostname information. This acts as an 
        acknolwedgement for the client and Provenance so that communication can start
        :param raw_request: the request found in :module: socketserver.UDPserver
        :return: A tuple containing the operating system and hostname of the client
        """
        raise NotImplementedError("syncrhonize() not implemented in subclass.")