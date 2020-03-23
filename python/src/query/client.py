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
    # 2dd1012000010000000000010462696e6703636f6d00000100010000291000000000000000 (bing)
    # b121012000010000000000010866616365626f6f6b03636f6d00000100010000291000000000000000 (facebook)
    # a38301200001000000000001047562657203636f6d00000100010000291000000000000000(uber)
    print("Enter a valid dns message below(bytes):")
    while True:
        line = sys.stdin.readline().strip()
        
        if not line:
            break

        # Send data
        print(f'Sending "{line}" to ({conn.toString()})')
        sent = sock.sendto(bytearray.fromhex(line), (conn.getIp(), conn.getPort()))

        # Receive response
        print("Waiting for response...")
        while True:
            data, server = sock.recvfrom(4096)
            print(f'Received from {conn.toString()}: {data}')
            if len(data) < 4096:
                break