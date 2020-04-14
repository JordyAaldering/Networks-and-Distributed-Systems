from socket import socket, AF_INET, SOCK_STREAM


class BTCPSocket:
    def __init__(self, window, timeout):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.window = window
        self.timeout = timeout

    @staticmethod
    def in_checksum(data):
        """Return the Internet checksum of data."""
        pass
