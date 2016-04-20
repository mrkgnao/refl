import socket
import threading
import sys
import random
from threading import Thread

import utils
import custom_logging
from handler import Handler

def main():
    serv = Server("JRTI")
    serv.start()

class Server(Thread):
    """
    A Server object models an instance of a central server that accepts files
    from authenticated clients and backs them up immutably.

    Not using `socketserver` for . . . reasons.
    """
    def __init__(self, name):
        self.ssock = socket.socket()
        self.name = name
        self.logger = custom_logging.get_colored_logger(self.name)
        self.begin_listen(listen_queue_len)

    def begin_listen(self, listen_queue_len):
        port = load_config.get_server_port()
        self.ssock.bind(('127.0.0.1', port))
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
