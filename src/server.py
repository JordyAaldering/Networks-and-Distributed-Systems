#!/usr/local/bin/python3

import argparse

from btcp.socket.server_socket import BTCPServerSocket, SEGMENT_SIZE


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--window", help="Define bTCP window size", type=int, default=100)
    parser.add_argument("-t", "--timeout", help="Define bTCP timeout in milliseconds", type=int, default=100)
    parser.add_argument("-o", "--output", help="Where to store the file", default="file.out")
    args = parser.parse_args()

    s = BTCPServerSocket(args.window, args.timeout)
    try:
        s.listen()
    finally:
        s.close()
    
    with open(args.output, "wb") as f:
        for msg in s.history:
            f.write(msg.data)


if __name__ == '__main__':
    main()
