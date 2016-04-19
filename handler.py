import socket
import threading
import custom_logging
import utils
from threading import Thread

class Handler(Thread):
    """A Handler is an object that communicates with a client."""
    def __init__(self, conn, addr):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.logger = custom_logging.get_colored_logger(utils.addr_to_ident(addr))
        self.CHUNK_SIZE = 1024

    def thread_name(self):
        return threading.current_thread().name

    def run(self):
        data = str(self.conn.recv(1024), 'ascii')
        cur_thread = threading.current_thread()
        response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
        self.conn.sendall(response[::-1])
        self.recv_sized_msg()
        self.conn.shutdown(socket.SHUT_RDWR)

    """Receive a string of a specified length."""
    def recv_string(self, str_len):
        self.logger.info("Handler {} awaiting data of length {}".format(self.thread_name(), str_len))
        left, done, msg = str_len, 0, bytearray()
        while left > 0:
            actual_chunksize = min(self.CHUNK_SIZE, left)
            msg += self.conn.recv(actual_chunksize)
            left -= self.CHUNK_SIZE
            done = min(str_len, done + self.CHUNK_SIZE)

        if str_len < 50:
            self.logger.info("Handler {} received data {} of length {}".format(self.thread_name(), msg.decode(), str_len))
        else:
            self.logger.info("Handler {} received data of length {}".format(self.thread_name(), str_len))

        return bytes(msg)

    def recv_msg_size(self):
        return int(self.recv_string(4))

    def recv_sized_msg(self):
        msg_size_size = self.recv_msg_size()
        self.logger.debug("Size of msg_size: {}".format(msg_size_size))
        msg_size = int(self.recv_string(msg_size_size))
        self.logger.debug("msg_size: {}".format(msg_size))
        return self.recv_string(msg_size)
