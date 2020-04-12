# USE dig [HOST NAME] @127.0.0.1 +noedns
# Avoids "malformed" packages messages do to EDNS V0
# Due to changes to the original DNS protocol

# bing.com A 172.217.11.174(google.com)
# facebook.com A 151.101.129.140(reddit)
# uber.com A 13.33.229.129(lyft)

import socketserver
import re
from threading import currentThread
from sys import byteorder, getsizeof
from os import environ
from dotenv import load_dotenv
from codecs import decode, encode


load_dotenv()

PORT = environ['SERVER_PORT']

DNS_ZONE_MAP = {
    "bing.com": b'\xAC\xD9\x0B\xAE',
    "facebook.com": b'\x97\x65\x81\x8C',
    "uber.com": b'\x0D\x21\xE5\x81',
}


class Connection:
    def __init__(self, socket, client, thread):
        self.socket = socket
        self.client = client
        self.thread = thread

    def getSocket(self):
        return self.socket

    def getClientAddr(self):
        return self.client

    def getThread(self):
        return self.thread

    def res(self, data):
        self.socket.sendto(data, self.client)


class DNSMessage:
    def __init__(self, byte_msg):
        self.__parse_message(byte_msg)

    def __parse_message(self, byte_msg):
        self.__extract_header(byte_msg[0:12])
        self.__extract_question(byte_msg[12:])
        self.__build_answer()

    def __extract_header(self, byte_array):
        # Parse bits and extract DNS Header Data
        print("Header (bytes)::", byte_array)
        header_as_bytes = bytes(b'')
        message_id = byte_array[0:2]
        qrcode = 1  # Query => Response
        opcode = 0  # Standard Query
        aa = 1  # Authoritative Answer
        tc = 0  # Truncate
        rd = 1  # Recursion Desired
        ra = 1  # Recursion Available
        z = 0  # Zeros
        rcode = 0  # Response Code: error will be thrown if one exists

        question_records_count = byte_array[4:6]
        original_answer_records_count = byte_array[6:8]
        original_ns_records_count = byte_array[8:10]
        original_ar_records_count = byte_array[10:12]

        header_as_bytes += message_id
        # QR, OpCode, AA, TC, and RD bits(1000 0101)
        header_as_bytes += b'\x85'
        header_as_bytes += b'\x80'  # RA, Z, and RCode bits(1000 0000)
        header_as_bytes += question_records_count  # QD Count
        header_as_bytes += b'\x00\x01'  # ANCount(1 for now)
        header_as_bytes += b'\x00\x00'  # NSCount
        header_as_bytes += b'\x00\x00'  # ARCount

        print("header_as_bytes::", header_as_bytes)

        self.msg_header = {
            "bytes": header_as_bytes,
            "id": message_id,
            "qrcode": qrcode,
            "opcode": opcode,
            "aa": aa,
            "tc": tc,
            "rd": rd,
            "ra": ra,
            "qdcount": question_records_count,
            "ancount": original_answer_records_count,
            "nscount": original_ns_records_count,
            "arcount": original_ar_records_count
        }

        print("msg_header:::")
        print(self.msg_header)

    def __extract_question(self, byte_array):
        # Parse bits and extract DNS Question Data(Query)
        print("Question (bytes)::", byte_array)
        qname_bytes_offset = 0

        for byte in byte_array:
            if (byte == 0):
                break
            qname_bytes_offset += 8

        qname_bytes_offset = int(qname_bytes_offset // 8)
        qname = byte_array[0:qname_bytes_offset + 1]
        qtype = byte_array[qname_bytes_offset + 1:qname_bytes_offset + 3]
        qclass = byte_array[qname_bytes_offset + 3:qname_bytes_offset + 5]
        aa_records = byte_array[qname_bytes_offset + 5:]

        self.msg_question = {
            "bytes": byte_array,
            "qname": qname,
            "qtype": qtype,
            "qclass": qclass,
        }
        self.msg_authority = {}
        self.msg_additional = aa_records

        print("msg_question:::")
        print(self.msg_question)
        print("msg_authority:::")
        print(self.msg_authority)
        print("msg_additional:::")
        print(self.msg_additional)

    def __build_answer(self):
        # Builds answer section of the DNS Message
        new_qname = bytearray()

        for (index, byte) in enumerate(self.msg_question["qname"]):
            if (index == 0):
                continue
            if (byte == 0):
                continue
            if (byte != 0 and (byte < 33 or byte > 172)):
                new_qname.append(46)  # ASCII period
                continue
            new_qname.append(byte)

        qname_ascii = decode(new_qname.strip(), "ascii")
        domain_ip_tmp_map = {
            qname_ascii: b'\x00\x00\x00\x00'
        }

        for domain in DNS_ZONE_MAP.keys():
            if domain in domain_ip_tmp_map:
                domain_ip_tmp_map[domain] = DNS_ZONE_MAP[domain]

        self.msg_answer = {
            "name": self.msg_question["qname"],
            "type": b'\x00\x01',  # IP Address (Type A)
            "class": b'\x00\x01',  # Internet
            "ttl": b'\x00\x00\x00\x3C',  # 60 seconds(not cached)
            "rdlength": b'\x00\x04',  # 2 bytes for IP Addresses
            "rdata": domain_ip_tmp_map[qname_ascii],
        }

    def getMessage(self):
        return {
            "header": self.msg_header,
            "question": self.msg_question,
            "answer": self.msg_answer,
            "authority": self.msg_authority,
            "additional": self.msg_additional,
        }

    def toResponse(self):
        message = self.getMessage()
        res = bytearray(message["header"]["bytes"])
        res += message["question"]["bytes"]

        # Note: Handle multiple Answer RRs
        for answerBytes in message["answer"].values():
            for byte in answerBytes:
                res.append(byte)

        res += message["additional"]

        print("response:", res)
        return res

    def __display_bytes_as_bitstring(self, byte_msg):
        print(int.from_bytes(byte_msg, byteorder="big", signed=False))


class ThreadingUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    daemon_threads = True
    allow_reuse_address = True


class MainHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        conn = Connection(
            self.request[1], self.client_address, currentThread())
        print(
            f'Handling {conn.getClientAddr()}\'s request on {conn.getThread().getName()}')
        datagram = self.request[0]
        print("Original Datagram(bytes)::", datagram)
        dns_message = DNSMessage(datagram)
        conn.res(dns_message.toResponse())


with ThreadingUDPServer(('', int(PORT)), MainHandler) as server:
    print(f'server listening on port {PORT}')
    server.serve_forever()
