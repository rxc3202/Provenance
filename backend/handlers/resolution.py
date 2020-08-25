from dnslib import DNSRecord, QTYPE, TXT, DNSError, RR, CLASS
from backend.handlers.protocolhandler import ProtocolHandler
from util.structs import CommandType
from enum import Enum



class Records(Enum):
    """ The types of records the DNSHandler can currently encode """
    TXT = (QTYPE.TXT, TXT)

class Domains(Enum):
    """ The valid subdomains used as function indicators by Resolution """
    SYNC = "sync"    
    ENCRYPT = "encrypt"
    QUERY = "query"
    CONFIRM = "confirm"



class DNSHandler(ProtocolHandler):
    """ This is the Provenance Handler implementation for DNS beacons"""
    RESPONSES = {
        "sync": "SYNC-ACKNOWLEDGE",
        "noencrypt": "1:NONE",
    }

    def __init__(self, ip, socket):
        super().__init__(ip, socket)
        self.record_type = Records.TXT
        # TODO: set record type function
        self.latest_request_id = None

    def __repr__(self):
        return "DNS"

    def synchronize(self, raw_request, port):
        data = raw_request[0].strip()
        try:
            request = DNSRecord.parse(data)
            q = request.questions[0]
            query = str(q.get_qname()).split(".")
            if query[2] == Domains.SYNC.value:
                self.synchronized = True
                platform, hostname = query[0], query[1]
                self._send_control(request, port, Domains.SYNC.value)
            return (platform, hostname)
        except DNSError:
            self.logger.debug("Incorrectly formatted DNS Query. Skipping")
            return ("","")


    def handle_request(self, raw_request, port, cmd):
        data = raw_request[0].strip()
        try:
            request = DNSRecord.parse(data)
            if request.header.id != self.latest_request_id:
                # If opcode is a normal QUERY then procede
                opcode = request.header.get_opcode() 
                if opcode == 0: # STANDARD QUERY
                    self.latest_request_id = request.header.id
                    self._send_command(request, port, cmd)
                elif opcode == 1: # INVERSE QUERY (Deprecated)
                    pass
                elif opcode == 2: # SERVER STATUS REQUEST
                    pass
                elif opcode == 3: # RESERVED (NOT USED)
                    pass
                elif opcode == 4: # NOTIFY
                    pass
                elif opcode == 5: # 5 UPDATE
                    pass
                else:
                    pass
        except DNSError:
            self.logger.debug("Incorrectly formatted DNS Query. Skipping")

    def _send_command(self, request: DNSRecord, port: int, command: str):
        opcode = command.type
        cmd = command.command
        # get the type of record this beacon is ready to receive
        rr_type, rr_constructor = self.record_type.value
        # Generate skeleton question for packet
        command_packet = request.reply()
        # Generate the response to the question
        command_packet.add_answer(
            RR(
                rname=request.get_q().get_qname(),
                rtype=rr_type,
                rclass=CLASS.IN,
                rdata=rr_constructor(f"<{opcode.value}>:{cmd}"),
                ttl=1337))
        # send command
        if opcode != CommandType.NOP:
            self.logger.info(f"Sending '{cmd}' to {self.ip}")
        else:
            self.logger.debug(f"NOP sent to {self.ip}")
        self.socket.sendto(command_packet.pack(), (self.ip, port))


    def _send_control(self, request: DNSRecord, port: int, control: str):
        # get the type of record this beacon is ready to receive
        rr_type, rr_constructor = self.record_type.value
        # Generate skeleton question for packet
        command_packet = request.reply()
        # Generate the response to the question
        command_packet.add_answer(
            RR(
                rname=request.get_q().get_qname(),
                rtype=rr_type,
                rclass=CLASS.IN,
                rdata=rr_constructor(f"1:{self.RESPONSES[control]}"),
                ttl=1337))
        # send command
        self.logger.debug(f"Sending CONTROL packet to {self.ip}")
        self.socket.sendto(command_packet.pack(), (self.ip, port))
