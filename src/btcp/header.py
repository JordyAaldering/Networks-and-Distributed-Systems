from src.btcp.constants import HEADER_FORMAT
import struct
class Header:
    
    def __init__(self, seq_number: int, ack_number: int, flags: int, 
            window_size: int, data_length: int = 0, checksum: int = 0):
        self.seq_number = seq_number
        self.ack_number = ack_number
        self.flags = flags
        self.window_size = window_size
        self.data_length = data_length
        self.checksum = checksum

    def __bytes__(self):
        return struct.pack(HEADER_FORMAT, self.seq_number, self.ack_number,
            self.flags, self.window_size, self.data_length, self.checksum)

    @classmethod
    def from_bytes(cls, msg: bytes):
        return cls(*struct.unpack(HEADER_FORMAT, msg))

    @staticmethod
    def build_flags(ack: bool = False, syn: bool = False, fin: bool = False) -> int:
        return ack << 2 | syn << 1 | fin << 0

    def ack(self) -> bool:
        return self.flags >> 2 & 1 == 1
    
    def syn(self) -> bool:
        return self.flags >> 1 & 1 == 1

    def fin(self) -> bool:
        return self.flags >> 0 & 1 == 1
