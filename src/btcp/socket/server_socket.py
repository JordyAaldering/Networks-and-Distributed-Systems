from threading import Thread
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

        
        self.socket.bind((SERVER_IP, SERVER_PORT))
        self.socket.listen(8)

        self.connection = None
        self.history = []

    def lossy_layer_input(self, segment):
        """Called by the lossy layer from another thread whenever a segment arrives."""
        pass

    def listen(self):
        while True:
            if self.connection is None:
                self.connection, address = self.socket.accept()
                print(f"Server connecting: {address[0]}:{address[1]}")
                continue

            recv_packet = self.recv()

            if recv_packet.header.syn():
                self.accept(recv_packet)
            elif recv_packet.header.fin():
                self.disconnect(recv_packet)
                return

    def accept(self, recv_packet: Packet) -> bool:
        """Wait for the client to initiate a three-way handshake."""
        y = randrange(65536)

        x = self._acknowledge_handshake(y, recv_packet, syn=True)
        success = self._finish_handshake(x, y, syn=True)
        if not success:
            print("Server connection failure")
            return False

        print("Server connected successfully")
        return True

    def disconnect(self, recv_packet: Packet) -> bool:
        print(f"Server disconnecting")

        y = randrange(65536)
        x = self._acknowledge_handshake(y, recv_packet, fin=True)

        success = self._finish_handshake(x, y, fin=True)
        if not success:
            print("Server disconnect failure")
            return False

        print("Server disconnected successfully")
        self.connection = None
        return True

    def recv(self) -> Packet:
        """Send any incoming data to the application layer."""
        msg = self.connection.recv(SEGMENT_SIZE)
        recv_packet = Packet.from_bytes(msg)
        self.history.append(recv_packet)

        print(f"Server recv packet: {str(recv_packet)}")
        return recv_packet

    def close(self):
        """Clean up any state."""
        self.lossy_layer.destroy()
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        self.socket.close()

    def _acknowledge_handshake(self, y: int, recv_packet: Packet, syn=False, fin=False) -> int:
        x = recv_packet.header.seq_number

        send_header = Header(y, x + 1, Header.build_flags(syn=syn, fin=fin, ack=True), self.window)
        send_packet = Packet(send_header, bytes())
        send_packet.calculate_checksum()

        self.connection.send(bytes(send_packet))
        print(f"Server send packet: {str(send_packet)}")
        return x

    def _finish_handshake(self, x: int, y: int, syn=False, fin=False) -> bool:
        try:
            recv_packet = self.recv()
        except TimeoutException as e:
            print(f"Socket timeout: {e}")
            return False

        if syn and not recv_packet.header.syn():
            print("Server handshake error: incorrect flag | expected SYN = True")
            return False
        if fin and not recv_packet.header.fin():
            print("Server handshake error: incorrect flag | expected FIN = True")
            return False
        if not recv_packet.header.ack():
            print("Server handshake error: incorrect flag | expected ACK = True")
            return False

        if x + 1 != recv_packet.header.seq_number:
            print(f"Client handshake error: incorrect SYN  | expected {x + 1}, got {recv_packet.header.seq_number}")
            return False
        if y + 1 != recv_packet.header.ack_number:
            print(f"Client handshake error: incorrect ACK  | expected {y + 1}, got {recv_packet.header.ack_number}")
            return False

        return True
