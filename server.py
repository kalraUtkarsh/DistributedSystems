import os
import sys
import socket
import argparse
import itertools
from threading import Thread


clients = []


# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock


    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()

    def run(self):
        while True:
            # First 4 bytes are for the file name length
            data = self.sock.recv(4)
            name_length = int.from_bytes(data, 'little')
            name = self.sock.recv(name_length).decode()

            # Name collision?
            if os.path.exists(name):
                base_name = '.'.join(name.split('.')[:-1])
                ext = name.split('.')[-1]
                for i in itertools.count(1):
                    new_name = f'{base_name} ({i}).{ext}'
                    if not os.path.exists(new_name):
                        break
                name = new_name

            with open(name, 'wb') as file:
                while data := self.sock.recv(1024):    # Note: Walrus operator available only in Python 3.8+
                    file.write(data)
                self._close()
                return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Receive files.')
    parser.add_argument('port', metavar='PORT', type=int, help='a port number to listen on')
    args = parser.parse_args()
    port = args.port

    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # reuse address; in OS address will be reserved after app closed for a while
    # so if we close and immediately start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # listen to all interfaces at the given port
    sock.bind(('', port))
    sock.listen()

    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        print(f'Got connection from {addr}')
        clients.append(con)

        # start new thread to deal with client
        ClientListener(con).start()