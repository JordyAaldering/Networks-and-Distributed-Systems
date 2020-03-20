from select import select
import socket
import threading

from src.btcp.constants import *


def handle_incoming_segments(btcp_socket, event, udp_socket):
    """
    Continuously read from the socket. Whenever a segment arrives,
    call the lossy_layer_input method of the associated socket.
    When flagged, return from the function.
    """
    while not event.is_set():
        # We do not block here, because we might never check the loop condition in that case.
        r_list, w_list, e_list = select([udp_socket], [], [], 1)
        if r_list:
            segment = udp_socket.recvfrom(SEGMENT_SIZE)
            btcp_socket.lossy_layer_input(segment)


class LossyLayer:
    """
    The lossy layer emulates the network layer in that it provides bTCP with
    an unreliable segment delivery service between a and b. When the lossy layer is created,
    a thread is started that calls handle_incoming_segments.
    """

    def __init__(self, btcp_socket, a_ip, a_port, b_ip, b_port):
        self.bTCP_socket = btcp_socket
        self.b_ip = b_ip
        self.b_port = b_port

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind((a_ip, a_port))

        self.event = threading.Event()
        self.thread = threading.Thread(
            target=handle_incoming_segments,
            args=(self.bTCP_socket, self.event, self.udp_socket))
        self.thread.start()

    def destroy(self):
        """Flag the thread that it can stop and close the socket."""
        self.event.set()
        self.thread.join()
        self.udp_socket.close()

    def send_segment(self, segment):
        """Put the segment into the network."""
        self.udp_socket.sendto(segment, (self.b_ip, self.b_port))
