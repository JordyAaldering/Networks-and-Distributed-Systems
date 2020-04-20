from random import randrange
from socket import timeout as TimeoutException

from src.btcp.constants import *
from src.btcp.header import Header
from src.btcp.lossy_layer import LossyLayer
from src.btcp.packet import Packet
from src.btcp.socket.btcp_socket import BTCPSocket


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
        x = randrange(65536)

        self.socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Client connected: {SERVER_IP}:{SERVER_PORT}")

        for i in range(5):
            header = Header(x, 0, Header.build_flags(syn=True), self.window)
            packet = Packet(header, bytes())

            self.socket.send(bytes(packet))
            print(f"Client send packet: {str(packet)}")

            try: 
                msg = self.socket.recv(HEADER_SIZE)
            except TimeoutException as e:
                print(f"Socket timeout: {e}")
                x += 1
                continue

            recv_packet = Packet.from_bytes(msg)
            print(f"Client recv packet: {str(recv_packet)}")

            if x + 1 != recv_packet.header.ack_number:
                print("ACK not x + 1")
                continue
            if not recv_packet.header.syn():
                print("SYN flag not set")
                continue
            if not recv_packet.header.ack():
                print("ACK flag not set")
                continue

            y = recv_packet.header.seq_number
            header = Header(x + 1, y + 1, Header.build_flags(syn=True, ack=True), self.window)
            packet = Packet(header, bytes())

            self.socket.send(bytes(packet))
            print(f"Client send packet: {str(packet)}")

            break

    def send(self, data: bytes):
        """Send data originating from the application in a reliable way to the server.""" 
        header = Header(0, 0, 0, self.window, len(data))
        packet = Packet(header, data)
        self.socket.send(bytes(packet))

    def disconnect(self):
        """Perform a handshake to terminate a connection."""
        pass

    def close(self):
        """Clean up any state."""
        self.lossy_layer.destroy()
        self.socket.close()


