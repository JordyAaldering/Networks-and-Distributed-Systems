from random import randrange
from socket import timeout as TimeoutException

from btcp.constants import *
from btcp.header import Header
from btcp.lossy_layer import LossyLayer
from btcp.packet import Packet
from btcp.socket.btcp_socket import BTCPSocket


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

    def connect(self, ip: str, port: int, tries=5) -> bool:
        """Perform a three-way handshake to establish a connection."""
        self.socket.connect((ip, port))
        print(f"Client connecting: {ip}:{port}")

        x = randrange(65536)

        for i in range(tries):
            success, recv_packet = self._initiate_handshake(x, syn=True)
            if success:
                self._acknowledge_handshake(x, recv_packet, syn=True)
                print("Client connected successfully")
                return True

            x += 1

        print("Client connection failure")
        return False

    def send(self, data: bytes):
        """Send data originating from the application in a reliable way to the server."""
        send_header = Header(0, 0, 0, self.window, len(data))
        send_packet = Packet(send_header, data)
        send_packet.calculate_checksum()
        self.socket.send(bytes(send_packet))

    def disconnect(self, tries=5):
        """Perform a handshake to terminate a connection."""
        print("Client disconnecting")

        x = randrange(65536)

        for i in range(tries):
            success, recv_packet = self._initiate_handshake(x, fin=True)
            if success:
                self._acknowledge_handshake(x, recv_packet, fin=True)
                print("Client disconnected successfully")
                return True

            x += 1

        print("Client disconnect failure")
        return False

    def close(self):
        """Clean up any state."""
        self.lossy_layer.destroy()
        self.socket.close()

    def _initiate_handshake(self, x: int, syn=False, fin=False) -> (bool, Packet):
        send_header = Header(x, 0, Header.build_flags(syn=syn, fin=fin), self.window)
        send_packet = Packet(send_header, bytes())
        send_packet.calculate_checksum()

        self.socket.send(bytes(send_packet))
        print(f"Client send packet: {str(send_packet)}")

        try:
            msg = self.socket.recv(HEADER_SIZE)
            recv_packet = Packet.from_bytes(msg)
            print(f"Client recv packet: {str(recv_packet)}")
        except TimeoutException as e:
            print(f"Socket timeout: {e}")
            return False, None

        if syn and not recv_packet.header.syn():
            print("Client handshake error: incorrect flag | expected SYN = True")
            return False, None
        if fin and not recv_packet.header.fin():
            print("Client handshake error: incorrect flag | expected FIN = True")
            return False, None
        if not recv_packet.header.ack():
            print("Client handshake error: incorrect flag | expected ACK = True")
            return False, None

        if x + 1 != recv_packet.header.ack_number:
            print(f"Client handshake error: incorrect ACK  | expected {x + 1}, got {recv_packet.header.ack_number}")
            return False, None

        return True, recv_packet

    def _acknowledge_handshake(self, x: int, recv_packet: Packet, syn=False, fin=False):
        y = recv_packet.header.seq_number

        send_header = Header(x + 1, y + 1, Header.build_flags(syn=syn, fin=fin, ack=True), self.window)
        send_packet = Packet(send_header, bytes())
        send_packet.calculate_checksum()

        self.socket.send(bytes(send_packet))
        print(f"Client send packet: {str(send_packet)}")
