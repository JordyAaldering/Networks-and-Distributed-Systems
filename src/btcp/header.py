import struct

from btcp.constants import HEADER_FORMAT


class Header:

    def __init__(self, seq_number: int, ack_number: int, flags: int,
                 window: int, data_length: int = 0, checksum: int = 0):
        self.seq_number = seq_number
        self.ack_number = ack_number
        self.flags = flags
        self.window = window
        self.data_length = data_length
        self.checksum = checksum

    def __bytes__(self):
        return struct.pack(HEADER_FORMAT,
                           self.seq_number,
                           self.ack_number,
                           self.flags,
                           self.window,
                           self.data_length,
                           self.checksum)

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

    def __str__(self):
        return f"{self.seq_number:05}, {self.ack_number:05} | " \
               f"ACK: {self.ack():d}, SYN: {self.syn():d}, FIN: {self.fin():d} | " \
               f"{self.checksum:05}"
