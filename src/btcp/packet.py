import binascii

from src.btcp.exceptions import ChecksumsNotEqual
from src.btcp.header import Header
from src.btcp.constants import HEADER_SIZE

# Explanation of checksum: https://tools.ietf.org/html/rfc1071
# Calculating checksum: https://www.bitforestinfo.com/2018/01/python-codes-to-calculate-tcp-checksum.html

class Packet:

    def __init__(self, header: Header, data: bytes):
        self.header = header
        self.data = data

    def __bytes__(self):
        self.header.checksum = 0
        checksum = binascii.crc32(bytes(self.header) + self.data)
        self.header.checksum = checksum

        return bytes(self.header) + self.data

    @classmethod
    def from_bytes(cls, msg: bytes):
        header = Header.from_bytes(msg[:HEADER_SIZE])
        checksum = header.checksum # before the data is sent

        header.checksum = 0
        if checksum != binascii.crc32(msg):
            raise ChecksumsNotEqual
        
        return cls(header, msg[HEADER_SIZE:])
