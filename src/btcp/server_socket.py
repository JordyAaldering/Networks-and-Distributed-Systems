from src.btcp.btcp_socket import BTCPSocket
from src.btcp.constants import *
from src.btcp.lossy_layer import LossyLayer


class BTCPServerSocket(BTCPSocket):
    """A server application makes use of the services provided by bTCP by calling accept, recv, and close."""

    def __init__(self, window, timeout):
        super().__init__(window, timeout)
        self.lossy_layer = LossyLayer(self, SERVER_IP, SERVER_PORT, CLIENT_IP, CLIENT_PORT)

    def lossy_layer_input(self, segment):
        """Called by the lossy layer from another thread whenever a segment arrives."""
        pass

    def accept(self):
        """Wait for the client to initiate a three-way handshake."""
        pass

    def recv(self):
        """Send any incoming data to the application layer."""
        pass

    def close(self):
        """Clean up any state."""
        self.lossy_layer.destroy()
