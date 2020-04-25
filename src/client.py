#!/usr/local/bin/python3

import argparse

from btcp.constants import *
from btcp.socket.client_socket import BTCPClientSocket


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--window", help="Define bTCP window size", type=int, default=100)
    parser.add_argument("-t", "--timeout", help="Define bTCP timeout in milliseconds", type=int, default=100)
    parser.add_argument("-i", "--input", help="File to send", default="file.in")
    args = parser.parse_args()

    s = BTCPClientSocket(args.window, args.timeout)
    try:
        s.connect(SERVER_IP, SERVER_PORT)
        with open(args.input, "rb") as f:
            s.send(f.read())
        s.disconnect()
    finally:
        s.close()


if __name__ == '__main__':
    main()
