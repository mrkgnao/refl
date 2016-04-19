import socket
import threading
import sys
import random
import load_config
import utils
import custom_logging
from handler import Handler

def main():
    serv = Server("Server")
    serv.start()

class Server(object):
    """
    A Server object models an instance of a central server that accepts files
    from authenticated clients and backs them up immutably.

    Not using `socketserver` for . . . reasons.
    """
    def __init__(self, ident):
        self.ssock = socket.socket()
        self.ident = ident
        self.logger = custom_logging.get_colored_logger(self.ident)

    def start(self, listen_queue_len=10):
        self.begin_listen(listen_queue_len)
        self.mainloop()

    def begin_listen(self, listen_queue_len):
        port = load_config.get_server_port()
        self.ssock.bind(('127.0.0.1', port))
        self.ssock.listen(listen_queue_len)
        self.logger.info("Server listening on port {}".format(port))

    def mainloop(self):
        while True:
            try:
                self.accept_and_respond()
            except KeyboardInterrupt:
                self.logger.critical("Interrupted by user. Exiting.")
                sys.exit(0)

    def accept_and_respond(self):
        conn, addr = self.ssock.accept()
        self.logger.debug("Client {} connected".format(utils.addr_to_ident(addr)))
        hdl = Handler(conn, addr)
        hdl.start()

if __name__ == '__main__':
    main()
