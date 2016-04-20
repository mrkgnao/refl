import socket
import threading
import sys
import random
from threading import Thread

import utils
import custom_logging
import config.settings as settings
from handler import Handler

def main():
    serv = Server("JRTI")
    serv.start()

class Server(Thread):
    """
    A Server object models an instance of a central server that runs on its own
    thread and accepts files from authenticated clients and backs them up immutably.

    Not using `socketserver` for . . . reasons.
    """
    def __init__(self, name="Ye olde server"):
        super().__init__()
        # Create the server socket
        self.ssock = socket.socket()
        # Menial work
        self.name = name
        self.logger = custom_logging.get_colored_logger(self.name)
        # Begin listening for incoming connections.
        self.begin_listen(settings.SERVER_LISTEN_QUEUE_MAXLEN)

    def begin_listen(self, listen_queue_len):
        addr = (host, port) = settings.SERVER_ADDR
        self.ssock.bind(addr)
        self.ssock.listen(listen_queue_len)
        self.logger.info("Server listening on port {}".format(port))

    def run(self):
        while True:
            try:
                conn, addr = self.ssock.accept()
                self.logger.debug("Client {} connected".format(utils.addr_to_ident(addr)))
                hdl = Handler(conn, addr)
                hdl.start()
            except KeyboardInterrupt:
                self.logger.critical("Interrupted by user. Exiting.")
                self.ssock.shutdown(socket.SHUT_RDWR)
                self.ssock.close()
                sys.exit(0)

if __name__ == '__main__':
    main()
