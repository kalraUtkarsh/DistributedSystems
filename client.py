import os
import sys
import socket
import argparse


def format_size(size: int) -> str:
    '''Given a file size in bytes, returns a human-readable 
        representation of that size (as a string) with appropriate units.'''
    for unit in ['B', 'KiB', 'MiB', 'GiB']:
        if size < 1024:
            break
        size /= 1024.0
    return f"{size:3.2f} {unit}"


parser = argparse.ArgumentParser(description='Send files using sockets.')
parser.add_argument('file_name', help='The path to the file to send')
parser.add_argument('address', help='The address to which to send the file')
parser.add_argument('port', type=int, help='The port number to send to')

args = parser.parse_args()
port: int      = args.port
address: str   = args.address
file_name: str = args.file_name

s = socket.socket()
s.connect((address, port))

with open(file_name, 'rb') as file:
    file_name_bytes = file_name.encode()
    byte_count = len(file_name_bytes)
    file_size = os.path.getsize(file_name)

    s.send(byte_count.to_bytes(4, 'little'))
    s.send(file_name_bytes)

    print(f'Sending "{file_name}" to {address}:{port}...')
    sent = 0  # To keep track of how many bytes have been actually sent
    while content := file.read(1024):    # Note: Walrus operator available only in Python 3.8+
        sent += s.send(content)
        ratio = sent / file_size
        bar_width = 40
        square_count = int(ratio * bar_width)
        bar = '■' * square_count
        spaces = ' ' * (bar_width - square_count)
        print(f'Progress: [{bar}{spaces}] {100*ratio:.2f}% ({format_size(sent)} / {format_size(file_size)})', end='\r' if ratio < 1 else '\n')

    s.close()
    print('File sent successfully!')