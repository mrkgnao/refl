import socket
import threading
import sys
from time import time

import utils
import custom_logging
import config.settings as settings

def main():
    if len(sys.argv) < 1:
        NUM_MB_TO_SEND = 200
    else:
        NUM_MB_TO_SEND = int(sys.argv[1])
        custom_logging.logger.debug(NUM_MB_TO_SEND)
    lst = []
    t = time()
    for i in range(10):
        c = Client(str(i))
        c.send_sized_msg(("0123456789")*100000 * NUM_MB_TO_SEND) #1e6 bytes

    t = time() - t
    custom_logging.logger.info("Send took {} s".format(t))

class Client(object):
    """
    The Client class models a single client system that submits files for backup
    to the central server.
    """
    def __init__(self, ident):
        self.sock = socket.socket()
        self.ident = ident
        self.setup_from_config()
        self.CHUNK_SIZE = 1024
        self.logger = custom_logging.get_colored_logger()

    """Load settings from config file."""
    def setup_from_config(self):
        host = settings.SERVER_HOST
        port = settings.SERVER_PORT
        self.serv = (host, port)
        self.sock.connect(self.serv)

    """Encode and send a string through a socket."""
    def send(self, msg):
        self.sock.sendall(msg.encode())

    def send_sized_msg(self, msg, send_hash=True, retry=5):
        msg = msg.encode()
        msg_len = len(msg)
        s_msg_len = len(str(msg_len))

        # The order is:
        # size_size, size, msg, hash
        self.sock.sendall(str(s_msg_len).zfill(4).encode())
        self.sock.sendall(str(msg_len).encode())
        self.sock.sendall(msg)
        self.sock.sendall(utils.get_hash(msg).encode())

    """Receive a string from the server."""
    def recv(self):
        return self.sock.recv(1024).decode()

    def send_file(self, filepath):
        f = open(filepath, mode='rb')

        file_len = os.path.getsize(filepath)
        bytes_left, bytes_sent = file_len, 0

        # Pre-send the number of bytes in the file, so that the handler knows
        # what to expect.
        self.send(str(file_len))
        l = f.read(self.CHUNK_SIZE)
        while l:
            self.send(l)
            bytes_left -= max(0, bytes_left - self.CHUNK_SIZE)
            bytes_sent = file_len - bytes_left
            self.logger.info("sent {} of total {}".format(bytes_sent, file_len))
            l = f.read(CHUNK_SIZE)
        self.logger.info("Done sending.")

if __name__ == '__main__':
    main()
