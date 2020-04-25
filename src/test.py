import sys
import unittest

from threading import Thread
from argparse import ArgumentParser
from subprocess import Popen, PIPE

from btcp.constants import *
from btcp.socket.client_socket import BTCPClientSocket
from btcp.socket.server_socket import BTCPServerSocket

window = 100
timeout = 100

INTF = "lo"
NETEM_ADD = "sudo tc qdisc add dev {} root netem".format(INTF)
NETEM_CHANGE = "sudo tc qdisc change dev {} root netem {}".format(INTF, "{}")
NETEM_DEL = "sudo tc qdisc del dev {} root netem".format(INTF)


def run_command(command, cwd=None, shell=True):
    """ Run command with no output piping. """
    try:
        process = Popen(command, cwd=cwd, shell=shell)
        print(str(process))
    except Exception as inst:
        print(f"1. Problem running command:\n\t{str(command)}\n\t{str(inst)}")
        return

    # Wait for the process to end.
    process.communicate()

    if process.returncode:
        print(f"2. Problem running command:\n\t{str(command)} {process.returncode}")


def run_command_with_output(command, input=None, cwd=None, shell=True):
    """ Run command and retrieve output. """
    try:
        process = Popen(command, cwd=cwd, shell=shell, stdin=PIPE, stdout=PIPE)
    except Exception:
        print(f"Problem running command:\n\t{str(command)}")
        return None

    # No pipes set for stdin, stdout, and stdout streams; so does effectively only just wait for process ends.
    [std_out_data, std_err_data] = process.communicate(input)

    if process.returncode:
        print(f"{std_err_data}\nProblem running command:\n\t{str(command)} {process.returncode}")

    return std_out_data


class TestFramework(unittest.TestCase):
    def setUp(self):
        """ Prepare for testing. """
        run_command(NETEM_ADD)
        # self.server = BTCPServerSocket(window, timeout)

    def tearDown(self):
        """ Clean up after testing. """
        run_command(NETEM_DEL)

    def test_ideal_network(self):
        """ Reliability over an ideal src. """
        # Setup environment. Nothing to set.

        self._test_client()

    def test_flipping_network(self):
        """ Reliability over network with bit flips which sometimes results in lower layer packet loss. """
        # Setup environment.
        run_command(NETEM_CHANGE.format("corrupt 1%"))

        self._test_client()

    def test_duplicates_network(self):
        """ Reliability over network with duplicate packets. """
        # Setup environment.
        run_command(NETEM_CHANGE.format("duplicate 10%"))

        self._test_client()

    def test_lossy_network(self):
        """ Reliability over network with packet loss. """
        # Setup environment.
        run_command(NETEM_CHANGE.format("loss 10% 25%"))

        self._test_client()

    def test_reordering_network(self):
        """ Reliability over network with packet reordering. """
        # Setup environment.
        run_command(NETEM_CHANGE.format("delay 20ms reorder 25% 50%"))

        self._test_client()

    def test_delayed_network(self):
        """ Reliability over network with delay relative to the timeout value. """
        # Setup environment.
        run_command(NETEM_CHANGE.format("delay " + str(timeout) + "ms 20ms"))

        self._test_client()

    def test_all_bad_network(self):
        """ Reliability over network with all of the above problems. """
        # Setup environment.
        run_command(NETEM_CHANGE.format("corrupt 1% duplicate 10% loss 10% 25% delay 20ms reorder 25% 50%"))

        self._test_client()

    def _test_client(self):
        # Launch localhost client connecting to server.
        client = BTCPClientSocket(window, timeout)
        client.connect(SERVER_IP, SERVER_PORT)

        # Client sends content to server.
        client.send(bytes("Hello, World!", ENCODING))

        # Server receives content from client.
        packet = self.server.recv(HEADER_SIZE)

        # Content received by server matches the content sent by client.
        assert packet.data.decode(ENCODING) == "Hello, World!"
        client.disconnent()
        client.close()


if __name__ == "__main__":
    # Parse command line arguments.
    parser = ArgumentParser(description="bTCP tests")
    parser.add_argument("-w", "--window", help="Define bTCP window size used", type=int, default=window)
    parser.add_argument("-t", "--timeout", help="Define the timeout value used (ms)", type=int, default=timeout)
    args, extra = parser.parse_known_args()

    window = args.window
    timeout = args.timeout

    # Pass the extra arguments to unittest.
    sys.argv[1:] = extra

    # Start test suite.
    unittest.main()
