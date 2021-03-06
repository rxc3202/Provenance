from abc import ABC, abstractmethod
from enum import Enum
import logging
from util.structs import Command
from socket import socket
from typing import Union


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
    def synchronize(self, raw_request, port: int) -> Union[tuple, None]:
        """
        A method that handles the initial synchronization between Provenance and
        the beacon to establish OS and hostname information. This acts as an 
        acknolwedgement for the client and Provenance so that communication can start
        :param raw_request: the request found in :module: socketserver.UDPserver. In order
        to signal for Provenance to change to the next state: ENCRYPT, this must return
        a tuple containing hostname and OS information
        :param port: the request found in :module: socketserver.UDPserver
        :return: A tuple containing the operating system and hostname of the client
        """
        raise NotImplementedError("syncrhonize() not implemented in subclass.")

    @abstractmethod
    def encrypt(self, raw_request, port: int, key: str) -> int:
        """
        A method that handles the response to the encrypt request from the beacon.
        This will take the raw requested forwarded from the network and then
        send the encryption key. This function must tell Provenance the state
        to go to next as described below:

        SYNC    -> 0
        ENCRYPT -> 1
        READY   -> 2

        If the server needs to reqreuest information from the beacon and needs to
        send the key back, then respond with 0.

        If the server needs to maintain the encrypt state return 1

        If the server can proceed accepting normal queries, return 2
        """
        raise NotImplementedError("respond() not implemented in subclass.")


    @abstractmethod
    def respond(self, raw_request, port: int, cmd: Command) -> int:
        """
        A method that handles the response to normal command queries. This will take
        the raw requested forwarded from the network and then send the next command
        in the queue. This function must tell Provenance the state
        to go to next as described below:

        SYNC    -> 0
        ENCRYPT -> 1
        READY   -> 2

        If the server needs to reqreuest information from the beacon and needs to
        send the key back, then respond with 0.

        If the server needs to return to the encrypt state return 1

        If the server can proceed accepting normal queries, return 2
        """
        raise NotImplementedError("respond() not implemented in subclass.")
