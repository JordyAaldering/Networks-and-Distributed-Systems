from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from btcp.exceptions import InvalidChecksum


class BTCPSocket:
    def __init__(self, window, timeout):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.settimeout(timeout)

        self.window = window
        self.timeout = timeout

    @staticmethod
    def calculate_checksum(data: bytes) -> int:
        """Return the Internet checksum of data."""
        s = 0
        data = str(data)
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                a = ord(data[i])
                b = ord(data[i + 1])
                s = s + (a + (b << 8))
            elif i + 1 == len(data):
                s += ord(data[i])
            else:
                raise InvalidChecksum()

        s = s + (s >> 16)
        s = ~s & 0xffff
        return s
