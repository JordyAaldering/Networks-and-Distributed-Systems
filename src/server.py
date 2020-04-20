#!/usr/local/bin/python3

import argparse

from src.btcp.socket.server_socket import BTCPServerSocket


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--window", help="Define bTCP window size", type=int, default=100)
    parser.add_argument("-t", "--timeout", help="Define bTCP timeout in milliseconds", type=int, default=100)
    parser.add_argument("-o", "--output", help="Where to store the file", default="output.file")
    args = parser.parse_args()

    s = BTCPServerSocket(args.window, args.timeout)

    # TODO Write your file transfer server code here using
    #  your BTCPServerSocket's accept, and recv methods.
    print("Start accept loop")
    s.accept()
    print("Finish accept loop")

    msg = ''
    while True:
        data = s.recv()
        if len(data) <= 0:
            break
        msg += data.decode("utf-8")

    print(msg)
    s.close()


if __name__ == '__main__':
    main()
