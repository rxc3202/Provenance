from dnslib import DNSRecord, QTYPE, TXT, AAAA, DNSError, RR, CLASS
from backend.handlers.protocolhandler import ProtocolHandler
from util.structs import CommandType, Command
from enum import Enum
import logging



class Records(Enum):
    """ The types of records the DNSHandler can currently encode """
    TXT = (QTYPE.TXT, TXT, 253)
    AAAA = (QTYPE.AAAA, AAAA, 13)

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
        """
        See protocolhandler.py
        """
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
            self.logger.debug(f"[{self.ip}] synchronize: Packet Malformed")
        return ""

    def encrypt(self, raw_request, port, key):
        """
        See protocolhandler.py
        """
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
                self.logger.debug(f"{self.ip}: Client not in ENCRYPT. Falling back to SYNC")
                return 0

        except DNSError as e:
            self.logger.debug(f"[{self.ip}] encrypt: DNS Packet Malformed: {str(e)}")

        return 1

    def respond(self, raw_request, port, cmd):
        """
        See protocolhandler.py
        """
        data = raw_request[0].strip()
        try:
            # if request.header.id != self.latest_id used for triplicate packets on windows
            request = DNSRecord.parse(data)
            q = request.questions[0]
            query = str(q.get_qname()).split(".")[::-1]
            if query[3] != Domains.QUERY.value:
                # Return back to SYNC state, will perform SYNC-REQUEST
                self.logger.debug(f"{self.ip}: Client not in QUERY. Falling back to SYNC")
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
        except DNSError as e:
            self.logger.debug(f"[{self.ip}] respond: DNS Packet Malformed: {str(e)}")
        return 2

    def _send_command(self, record: DNSRecord, port: int, command: str):
        """
        Send control packets to the client
        """

        def TXT(rr_type, packet):
            cmd = command.command
            _, constructor, msg_size = Records.TXT.value
            chunks = [f"1:{cmd[i:i+msg_size]}" for i in range(0, len(cmd), msg_size)] 
            for chunk in chunks:
                answer = RR(
                        rname=record.get_q().get_qname(),
                        rtype=rr_type,
                        rclass=CLASS.IN,
                        rdata=constructor(chunk),
                        ttl=1337)
                packet.add_answer(answer)

        def AAAA(rr_type, packet):
            cmd = command.command
            _, constructor, msg_size = Records.AAAA.value
            chunks = [cmd[i:i+msg_size] for i in range(0, len(cmd), msg_size)]
            self.logger.debug(chunks)

            #opcode = 0 if command.type == CommandType.NOP else 3
            opcode = 3
            if opcode == 0:
                packet.add_answer(
                    RR(
                        rname=record.get_q().get_qname(),
                        rtype=rr_type,
                        rclass=CLASS.IN,
                        # Send a nop packet of seq num 0, and expected length 1
                        rdata=constructor([0, 1, 0] + [0 for _ in range(13)]),
                        ttl=1337))
            else:
                for i, chunk in enumerate(chunks):
                    #data = [opcode, i, len(chunks)] + [ord(c) for c in chunk]
                    data = [3, 1, 0] + [ord(c) for c in chunk] #currently doing edns
                    # Pad the data to 16 bytes
                    data += [0 for _ in range(16 - len(data))]
                    answer = RR(
                            rname=record.get_q().get_qname(),
                            rtype=rr_type,
                            rclass=CLASS.IN,
                            # 1st byte indicates data, second byte is seq number, 3rd is num transmission packets
                            rdata=constructor(data),
                            ttl=1337)
                    packet.add_answer(answer)
            

        rr_type = record.questions[0].qtype
        # Generate skeleton question for packet
        command_packet = record.reply()
        if rr_type == 16:
            TXT(rr_type, command_packet)
        elif rr_type == 28:
            AAAA(rr_type, command_packet)
        else:
            self.logger.debug("send_command: invalid record")
            pass

        # Reply
        self.socket.sendto(command_packet.pack(), (self.ip, port))

    def _send_control(self, record: DNSRecord, port: int, control: str):
        """
        Send control packets to the client
        """

        def TXT(rr_type):
            _, rr_constructor, _ = Records.TXT.value
            return RR(rname=record.get_q().get_qname(),
                rtype=rr_type,
                rclass=CLASS.IN,
                rdata=rr_constructor(f"1:{control}"),
                ttl=1337)

        def AAAA(rr_type):
            _, rr_constructor, _ = Records.AAAA.value
            return RR(rname=record.get_q().get_qname(),
                rtype=rr_type,
                rclass=CLASS.IN,
                rdata=rr_constructor([1, 1, 0, 104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100, 0, 0]),
                ttl=1337)

        rr_type = record.questions[0].qtype
        # Generate skeleton question for packet
        command_packet = record.reply()
        if rr_type == 16:
            command_packet.add_answer(TXT(rr_type))
        elif rr_type == 28:
            command_packet.add_answer(AAAA(rr_type))
        else:
            self.logger.debug("send_control: invalid record")
            pass

        # Reply
        self.socket.sendto(command_packet.pack(), (self.ip, port))
