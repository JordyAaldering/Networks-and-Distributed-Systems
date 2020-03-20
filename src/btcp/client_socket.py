from src.btcp.btcp_socket import BTCPSocket
from src.btcp.constants import *
from src.btcp.lossy_layer import LossyLayer


class BTCPClientSocket(BTCPSocket):
    """
    A client application makes use of the services provided
    by bTCP by calling connect, send, disconnect, and close.
    """

    def __init__(self, window, timeout):
        super().__init__(window, timeout)
        self.lossy_layer = LossyLayer(self, CLIENT_IP, CLIENT_PORT, SERVER_IP, SERVER_PORT)

    def lossy_layer_input(self, segment):
        """Called by the lossy layer from another thread whenever a segment arrives."""
        pass

    def connect(self):
        """Perform a three-way handshake to establish a connection."""
        pass

    def send(self, data):
        """Send data originating from the application in a reliable way to the server."""
        pass

    def disconnect(self):
        """Perform a handshake to terminate a connection."""
        pass

    def close(self):
        """Clean up any state."""
        self.lossy_layer.destroy()
