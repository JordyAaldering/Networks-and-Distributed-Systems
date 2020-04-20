from src.btcp.socket.btcp_socket import BTCPSocket
from random import randrange

from src.btcp.header import Header
from src.btcp.packet import Packet

from src.btcp.constants import *
from src.btcp.lossy_layer import LossyLayer


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
        print(f"Connected with {client[1][0]}:{str(client[1][1])}")

        msg = client[0].recv(HEADER_SIZE)
        recv_packet = Packet.from_bytes(msg)
        print(f"Receive packet: {recv_packet}")

        if not recv_packet.header.syn():
            print("SYN flag not set")
            return
        
        x = recv_packet.header.seq_number
        y = randrange(65536)

        header = Header(x + 1, y, Header.build_flags(syn=True, ack=True), self.window)
        packet = Packet(header, bytes())

        self.socket.sendto(packet, (CLIENT_IP, CLIENT_PORT))

        try: 
            msg = self.socket.recv(HEADER_SIZE)
        except:
            print("Socket timeout")
            return
        
        recv_packet = Packet.from_bytes(msg)
        if x + 1 != recv_packet.header.ack_number:
            print("ACK not x + 1")
            return
        if y + 1 != recv_packet.header.syn_number:
            print("ACK not x + 1")
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

    def recv(self) -> bytes:
        """Send any incoming data to the application layer."""
        return self.socket.recv()

    def close(self):
        """Clean up any state."""
        self.lossy_layer.destroy()
        self.socket.close()
