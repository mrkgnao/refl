import socket
import threading
import load_config
import codes

def main():
    client = Client("Soham's PC")
    client.send("Hi from " + client.ident)
    print(client.recv())
    while True:
        pass

class Client(object):
    """
    The Client class models a single client system that submits files for backup
    to the central server.
    """
    def __init__(self, ident):
        self.sock = socket.socket()
        self.ident = ident
        self.setup_from_config()

    """Load settings from config file."""
    def setup_from_config(self):
        host = load_config.get_server_host()
        port = load_config.get_server_port()
        self.serv = (host, port)
        self.sock.connect(self.serv)

    """Encode and send a string through a socket."""
    def send(self, msg):
        self.sock.sendall(msg.encode())

    """Receive a string from the server."""
    def recv(self):
        return self.sock.recv(1024).decode()

if __name__ == '__main__':
    main()
