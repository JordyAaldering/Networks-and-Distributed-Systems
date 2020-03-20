import sys
import unittest
from argparse import ArgumentParser
from subprocess import Popen, PIPE

timeout = 100
win_size = 100

INTF = "lo"
NETEM_ADD = "sudo tc qdisc add dev {} root netem".format(INTF)
NETEM_CHANGE = "sudo tc qdisc change dev {} root netem {}".format(INTF, "{}")
NETEM_DEL = "sudo tc qdisc del dev {} root netem".format(INTF)


def run_command(command, cwd=None, shell=True):
    """ Run command with no output piping. """
    try:
        process = Popen(command, shell=shell, cwd=cwd)
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
        # Default netem rule, does nothing.
        run_command(NETEM_ADD)

        # Launch localhost server.

    def tearDown(self):
        """ Clean up after testing. """
        # Clean the environment.
        run_command(NETEM_DEL)

        # Close server.

    def test_ideal_network(self):
        """ Reliability over an ideal src. """
        # Setup environment. Nothing to set.
        # Launch localhost client connecting to server.

        # Client sends content to server.

        # Server receives content from client.

        # Content received by server matches the content sent by client.

    def test_flipping_network(self):
        """ Reliability over network with bit flips which sometimes results in lower layer packet loss. """
        # Setup environment.
        run_command(NETEM_CHANGE.format("corrupt 1%"))

        # Launch localhost client connecting to server.

        # Client sends content to server.

        # Server receives content from client.

        # Content received by server matches the content sent by client.

    def test_duplicates_network(self):
        """ Reliability over network with duplicate packets. """
        # Setup environment.
        run_command(NETEM_CHANGE.format("duplicate 10%"))

        # Launch localhost client connecting to server.

        # Client sends content to server.

        # Server receives content from client.

        # Content received by server matches the content sent by client.

    def test_lossy_network(self):
        """ Reliability over network with packet loss. """
        # Setup environment.
        run_command(NETEM_CHANGE.format("loss 10% 25%"))

        # Launch localhost client connecting to server.

        # Client sends content to server.

        # Server receives content from client.

        # Content received by server matches the content sent by client.

    def test_reordering_network(self):
        """ Reliability over network with packet reordering. """
        # Setup environment.
        run_command(NETEM_CHANGE.format("delay 20ms reorder 25% 50%"))

        # Launch localhost client connecting to server.

        # Client sends content to server.

        # Server receives content from client.

        # Content received by server matches the content sent by client.

    def test_delayed_network(self):
        """ Reliability over network with delay relative to the timeout value. """
        # Setup environment.
        run_command(NETEM_CHANGE.format("delay " + str(timeout) + "ms 20ms"))

        # Launch localhost client connecting to server.

        # Client sends content to server.

        # Server receives content from client.

        # Content received by server matches the content sent by client.

    def test_all_bad_network(self):
        """ Reliability over network with all of the above problems. """

        # Setup environment.
        run_command(NETEM_CHANGE.format("corrupt 1% duplicate 10% loss 10% 25% delay 20ms reorder 25% 50%"))

        # Launch localhost client connecting to server.

        # Client sends content to server.

        # Server receives content from client.

        # Content received by server matches the content sent by client.


if __name__ == "__main__":
    # Parse command line arguments.
    parser = ArgumentParser(description="bTCP tests")
    parser.add_argument("-t", "--timeout", help="Define the timeout value used (ms)", type=int, default=timeout)
    parser.add_argument("-w", "--window", help="Define bTCP window size used", type=int, default=win_size)
    args, extra = parser.parse_known_args()

    timeout = args.timeout
    win_size = args.window

    # Pass the extra arguments to unittest.
    sys.argv[1:] = extra

    # Start test suite.
    unittest.main()
