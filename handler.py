import threading
from threading import Thread
from socketserver import BaseRequestHandler

class Handler(Thread):
    """A Handler is an object that communicates with a client."""
    def __init__(self, conn, addr):
        super().__init__()
        self.conn = conn
        self.addr = addr

    def run(self)
        data = str(self.conn.recv(1024), 'ascii')
        cur_thread = threading.current_thread()
        response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
        self.conn.sendall(response[::-1])
