class BTCPSocket:
    def __init__(self, window, timeout):
        self._window = window
        self._timeout = timeout

    @staticmethod
    def in_checksum(data):
        """Return the Internet checksum of data."""
        pass
