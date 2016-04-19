import socket
import threading
import custom_logging
import utils
import load_config
from time import time
from threading import Thread

class Handler(Thread):
    """A Handler is an object that communicates with a client."""
    def __init__(self, conn, addr):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.logger = custom_logging.get_colored_logger(utils.addr_to_ident(addr))
        self.CHUNK_SIZE = load_config.get_chunk_size()

    def thread_name(self):
        return threading.current_thread().name

    def run(self):
        self.logger.warning("Starting handler for client {}".format(utils.addr_to_ident(self.addr)))
        self.recv_sized_msg()
        self.conn.shutdown(socket.SHUT_RDWR)

    """Receive a string of a specified length."""
    def recv_string(self, str_len):
        self.logger.info("Handler {} awaiting data of length {}".format(self.thread_name(), str_len))
        t = time()
        left, done, msg = str_len, 0, bytearray()
        while left > 0:
            actual_chunksize = min(self.CHUNK_SIZE, left)
            msg += self.conn.recv(actual_chunksize)
            left -= self.CHUNK_SIZE
            done = min(str_len, done + self.CHUNK_SIZE)

        t = time() - t
        transfer_speed = (str_len / t) / 1024 # KB/s
        if str_len < 50:
            self.logger.info("Handler {} received data {} of length {}".format(self.thread_name(), msg.decode(), str_len))
        else:
            self.logger.info("Handler {} received data of length {} ({:.2f} KB/s)".format(
                self.thread_name(), str_len, transfer_speed))

        return bytes(msg)

    def recv_int(self, num_chars=4):
        return int(self.recv_string(num_chars))

    def recv_sized_msg(self):
        # This is hideous
        msg_size_size = self.recv_int()
        self.logger.debug("Size of msg_size: {}".format(msg_size_size))
        # What can I do?
        msg_size = self.recv_int(num_chars=msg_size_size)
        self.logger.debug("msg_size: {}".format(msg_size))

        msg = self.recv_string(msg_size)
        actual_hash = self.recv_string(56).decode()
        computed_hash = utils.get_sha224(msg)

        if actual_hash == computed_hash:
            self.logger.debug("Actual and computed hashes match (both {})".format(actual_hash))
        else:
            self.logger.error("Hash mismatch! Actual: {}, computed: {}".format(actual_hash, computed_hash))

        return msg
