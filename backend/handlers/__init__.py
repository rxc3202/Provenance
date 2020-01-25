import logging
from abc import ABC, abstractmethod


"""
An abstract class that defines the methods that need
to be implemented so that Provenance can handle the 
request being received with the correct protocol.
"""
class ProtocolHandler(ABC):

    @abstractmethod
    def handle_request(self, raw_request):
        raise "handle_request() not implemented in subclass."


    @abstractmethod
    def queue_command(self):
        raise "queue_command() not implemented in subclass."
