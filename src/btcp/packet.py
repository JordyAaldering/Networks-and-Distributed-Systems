from btcp.constants import HEADER_SIZE
from btcp.exceptions import ChecksumsNotEqual
from btcp.header import Header
from btcp.socket.btcp_socket import BTCPSocket


class Packet:

    def __init__(self, header: Header, data: bytes):
        self.header = header
        self.data = data

    def __bytes__(self):
        self.calculate_checksum()
        return bytes(self.header) + self.data

    def calculate_checksum(self) -> int:
        self.header.checksum = 0
        checksum = BTCPSocket.calculate_checksum(bytes(self.header) + self.data)
        self.header.checksum = checksum
        return checksum

    @classmethod
    def from_bytes(cls, msg: bytes):
        header = Header.from_bytes(msg[:HEADER_SIZE])
        checksum = header.checksum

        header.checksum = 0
        if checksum != BTCPSocket.calculate_checksum(bytes(header) + msg[HEADER_SIZE:]):
            raise ChecksumsNotEqual
        
        return cls(header, msg[HEADER_SIZE:])

    def __str__(self):
        return f"{str(self.header)} | '{self.data.decode('utf-8')}'"
