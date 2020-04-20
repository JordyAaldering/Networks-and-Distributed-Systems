#!/usr/local/bin/python3

import argparse

from src.btcp.socket.client_socket import BTCPClientSocket


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--window", help="Define bTCP window size", type=int, default=100)
    parser.add_argument("-t", "--timeout", help="Define bTCP timeout in milliseconds", type=int, default=100)
    parser.add_argument("-i", "--input", help="File to send", default="input.file")
    args = parser.parse_args()

    s = BTCPClientSocket(args.window, args.timeout)

    # TODO Write your file transfer client code using your implementation of
    #  BTCPClientSocket's connect, send, and disconnect methods.
    print("Start connect loop")
    s.connect()
    s.send(bytes("Hello, World!"))
    


if __name__ == '__main__':
    main()
