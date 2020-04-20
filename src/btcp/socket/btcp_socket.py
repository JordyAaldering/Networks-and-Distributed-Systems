from socket import socket, timeout, AF_INET, SOCK_STREAM

class BTCPSocket:
    def __init__(self, window, timeout):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.window = window
        self.timeout = timeout

    @staticmethod
    def checksum(data):
        """Return the Internet checksum of data.
        https://www.bitforestinfo.com/2018/01/python-codes-to-calculate-tcp-checksum.html"""
        s = 0
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                a = ord(data[i]) 
                b = ord(data[i + 1])
                s = s + (a + (b << 8))
            elif i + 1 == len(data):
                s += ord(data[i])
            else:
                raise Exception("Something Wrong here")

        s = s + (s >> 16)
        s = ~s & 0xffff
        return s
