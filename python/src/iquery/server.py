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
    "172.217.11.174": b'\x04\x62\x69\x6e\x67\x03\x63\x6f\x6d\x00',
    "151.101.129.140": b'\x08\x66\x61\x63\x65\x62\x6f\x6f\x6b\x03\x63\x6f\x6d\x00',
    "13.33.229.129": b'\x04\x75\x62\x65\x72\x03\x63\x6f\x6d\x00',
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
        opcode = 1  # Inverse query
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
        # QR, OpCode, AA, TC, and RD bits(1000 0001)
        header_as_bytes += b'\x89'
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
        # TODO: onverting answer into bytes
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
        print("qname_ascii:", qname_ascii)
        ip_domain_tmp_map = {
            qname_ascii: ""
        }

        for domain in DNS_ZONE_MAP.keys():
            if domain in ip_domain_tmp_map:
                ip_domain_tmp_map[domain] = DNS_ZONE_MAP[domain]

        # Needed because of invalid encoding for
        # the qname received from input stream

        arr_of_ip_bytes = bytearray()
        for x in qname_ascii.split('.'):
            arr_of_ip_bytes.append(int(x))

        self.msg_answer = {
            "name": ip_domain_tmp_map[qname_ascii],
            "type": b'\x00\x01',  # IP
            "class": b'\x00\x01',  # Internet
            "ttl": b'\x00\x00\x00\x3C',  # 60 seconds(not cached)
            "rdlength": b'\x00\x04',  # 2 bytes for IP Addresses
            "rdata": arr_of_ip_bytes
        }

        print("msg_answer:::")
        print(self.msg_answer)

    def getMessage(self):
        return {
            "header": self.msg_header,
            "question": self.msg_question,
            "answer": self.msg_answer,
            "authority": self.msg_authority,
            "additional": self.msg_additional
        }

    def toResponse(self, original_bytes):
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
        print(datagram.hex())
        dns_message = DNSMessage(datagram)
        conn.res(dns_message.toResponse(datagram))


with ThreadingUDPServer(('', int(PORT)), MainHandler) as server:
    print(f'server listening on port {PORT}')
    server.serve_forever()
