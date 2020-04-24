import threading
from random import randrange
from socket import timeout as TimeoutException

from btcp.constants import *
from btcp.header import Header
from btcp.lossy_layer import LossyLayer
from btcp.packet import Packet
from btcp.socket.btcp_socket import BTCPSocket


class BTCPServerSocket(BTCPSocket):
    """A server application makes use of the services provided by bTCP by calling accept, recv, and close."""

    def __init__(self, window, timeout):
        super().__init__(window, timeout)
        self.lossy_layer = LossyLayer(self, SERVER_IP, SERVER_PORT, CLIENT_IP, CLIENT_PORT)

        self.socket.bind(SERVER_ADDR)
        self.socket.listen(8)

        self.connection = None

        self.listenThread = threading.Thread(target=self.listen)
        self.listenThread.start()

    def lossy_layer_input(self, segment):
        """Called by the lossy layer from another thread whenever a segment arrives."""
        pass

    def listen(self):
        self.accept()

    def accept(self):
        """Wait for the client to initiate a three-way handshake."""
        client, address = self.socket.accept()
        print(f"Server connecting: {address}")

        msg = client.recv(HEADER_SIZE)
        recv_packet = Packet.from_bytes(msg)
        print(f"Server recv packet: {str(recv_packet)}")

        if not recv_packet.header.syn():
            print("Server handshake error: incorrect flag | expected SYN = True")
            return
        
        x = recv_packet.header.seq_number
        y = randrange(65536)

        header = Header(y, x + 1, Header.build_flags(syn=True, ack=True), self.window)
        packet = Packet(header, bytes())

        client.send(bytes(packet))
        print(f"Server send packet: {str(packet)}")

        try: 
            msg = client.recv(HEADER_SIZE)
            recv_packet = Packet.from_bytes(msg)
            print(f"Server recv packet: {str(recv_packet)}")
        except TimeoutException as e:
            print(f"Socket timeout: {e}")
            return

        if not recv_packet.header.syn():
            print("Server handshake error: incorrect flag | expected SYN = True")
            return
        if not recv_packet.header.ack():
            print("Server handshake error: incorrect flag | expected ACK = True")
            return

        if x + 1 != recv_packet.header.seq_number:
            print(f"Client handshake error: incorrect SYN  | expected {x + 1}, got {recv_packet.header.seq_number}")
            return
        if y + 1 != recv_packet.header.ack_number:
            print(f"Client handshake error: incorrect ACK  | expected {y + 1}, got {recv_packet.header.ack_number}")
            return
        
        print("Server connected successfully")
        self.connection = client

    def recv(self, size: int) -> Packet:
        """Send any incoming data to the application layer."""
        recv = self.connection.recv(size)
        packet = Packet.from_bytes(recv)
        print(f"Server recv packet: {str(packet)}")
        return packet

    def close(self):
        """Clean up any state."""
        self.lossy_layer.destroy()
        self.listenThread.join()
        self.socket.close()
