from random import randrange
from socket import timeout as TimeoutException

from src.btcp.constants import *
from src.btcp.header import Header
from src.btcp.lossy_layer import LossyLayer
from src.btcp.packet import Packet
from src.btcp.socket.btcp_socket import BTCPSocket


class BTCPServerSocket(BTCPSocket):
    """A server application makes use of the services provided by bTCP by calling accept, recv, and close."""

    def __init__(self, window, timeout):
        super().__init__(window, timeout)
        self.lossy_layer = LossyLayer(self, SERVER_IP, SERVER_PORT, CLIENT_IP, CLIENT_PORT)

        self.socket.bind((SERVER_IP, SERVER_PORT))
        self.socket.listen(8)

    def lossy_layer_input(self, segment):
        """Called by the lossy layer from another thread whenever a segment arrives."""
        pass

    def accept(self):
        """Wait for the client to initiate a three-way handshake."""
        client = self.socket.accept()
        print(f"Server connected: {client[1][0]}:{str(client[1][1])}")

        msg = client[0].recv(HEADER_SIZE)
        recv_packet = Packet.from_bytes(msg)
        print(f"Server recv packet: {str(recv_packet)}")

        if not recv_packet.header.syn():
            print("SYN flag not set")
            return
        
        x = recv_packet.header.seq_number
        y = randrange(65536)

        header = Header(y, x + 1, Header.build_flags(syn=True, ack=True), self.window)
        packet = Packet(header, bytes())

        client[0].send(bytes(packet))
        print(f"Server send packet: {str(packet)}")

        try: 
            msg = client[0].recv(HEADER_SIZE)
        except TimeoutException as e:
            print(f"Socket timeout: {e}")
            return
        
        recv_packet = Packet.from_bytes(msg)
        print(f"Server recv packet: {str(recv_packet)}")

        if x + 1 != recv_packet.header.seq_number:
            print("ACK not x + 1")
            return
        if y + 1 != recv_packet.header.ack_number:
            print("SYN not y + 1")
            return
        if not recv_packet.header.syn():
            print("SYN flag not set")
            return
        if not recv_packet.header.ack():
            print("ACK flag not set")
            return
        
        # should return a tuple (host,port) -> conn,addr = s.accept() -> new socket object
        #       used to communicate with the client, different socket than the listening
        return client

    def recv(self) -> Packet:
        """Send any incoming data to the application layer."""
        recv = self.socket.recv(1024)
        packet = Packet.from_bytes(recv)
        print(f"Server recv packet: {str(packet)}")
        return packet

    def close(self):
        """Clean up any state."""
        self.lossy_layer.destroy()
        self.socket.close()
