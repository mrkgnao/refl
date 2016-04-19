import socket
import threading
import load_config
import codes
import custom_logging

def main():
    client = Client("Soham's PC")
    client.send("Hi from " + client.ident)
    print(client.recv())
    client.send_sized_msg("asdf123"*2000000)

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

    def send_sized_msg(self, msg):
        msg_len = len(msg)
        s_msg_len = len(str(msg_len))
        self.sock.sendall(str(s_msg_len).encode())
        self.sock.sendall(str(msg_len).encode())
        self.sock.sendall(msg.encode())

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
