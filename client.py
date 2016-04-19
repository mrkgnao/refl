import socket
import threading
import load_config
import codes
import utils
import custom_logging

def main():
    lst = []
    for i in range(10):
        lst.append(Client(str(i)))

    for c in lst:
        c.send_sized_msg(("asdf" + c.ident)*100000)

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
        self.logger = custom_logging.get_colored_logger("Client")

    """Load settings from config file."""
    def setup_from_config(self):
        host = load_config.get_server_host()
        port = load_config.get_server_port()
        self.serv = (host, port)
        self.sock.connect(self.serv)

    """Encode and send a string through a socket."""
    def send(self, msg):
        self.sock.sendall(msg.encode())

    def send_sized_msg(self, msg, send_hash=True):
        msg_len = len(msg)
        s_msg_len = len(str(msg_len))

        # The order is:
        # size_size, size, msg, hash
        self.sock.sendall(str(s_msg_len).zfill(4).encode())
        self.sock.sendall(str(msg_len).encode())
        self.sock.sendall(msg.encode())
        self.sock.sendall(utils.get_sha224(msg.encode()).encode())

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
