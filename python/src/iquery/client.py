import sys
import socket
from codecs import encode


class Connection:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def getIp(self):
        return self.ip

    def getPort(self):
        return self.port

    def toString(self):
        return f'{self.ip}:{self.port}'


if (len(sys.argv) != 3):
    raise ValueError("Need IP of the machine running server it's Port")


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    conn = Connection(sys.argv[1], int(sys.argv[2]))
    # 55750120000100000000000103313732033231370231310331373400000100010000291000000000000000 (172.217.11.174)
    # b3a5012000010000000000010331353103313031033132390331343000000100010000291000000000000000 (151.101.129.140)
    # 3ed201200001000000000001023133023333033232390331323900000100010000291000000000000000 (13.33.229.129)
    print("Enter a valid dns message below(bytes):")
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        # Send data
        print(f'Sending "{line}" to ({conn.toString()})')
        
        # sent = sock.sendto(encode(line, "ascii"), (conn.getIp(), conn.getPort()))
        sent = sock.sendto(bytearray.fromhex(line), (conn.getIp(), conn.getPort()))

        # Receive response
        print("Waiting for response...")
        while True:
            data, server = sock.recvfrom(4096)
            print(f'Received from {conn.toString()}: {data}')
            if len(data) < 4096:
                break
