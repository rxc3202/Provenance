from socketserver import BaseRequestHandler
import backend.handlers as handlers


class IndividualClientHandler(BaseRequestHandler):
    """ Builtin Functions"""
    def __init__(self, request, client_address, server, handler=None):
        # Superclass initialization
        self.request = request
        self.client_address = client_address
        self.server = server

        # The model that tracks each controlled machine
        self.protocol_handler = handler or handlers.dns.DNSHandler(
            client_address[0], client_address[1], request[1]
        )


    """ BaseRequestHandler function """
    def handle(self):
        self.protocol_handler.handle_request(self.request)
        
