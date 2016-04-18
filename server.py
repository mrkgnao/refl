import socket
import threading
import sys
import random
import load_config

def main():
    serv = Server("Just Read The Instructions")
    serv.start()

class Server(object):
    """
    A Server object models an instance of a central server that accepts files
    from authenticated clients and backs them up immutably.
    """
    def __init__(self, ident):
        self.ssock = socket.socket()
        self.ident = ident

    def start(self, listen_queue_len=10):
        self.begin_listen(listen_queue_len)
        self.mainloop()

    def begin_listen(self, listen_queue_len):
        port = load_config.get_server_port()
        self.ssock.bind(('127.0.0.1', port))
        self.ssock.listen(listen_queue_len)
        print("Server listening on port {}".format(port))

    def mainloop(self):
        while True:
            try:
                self.accept_and_respond()
            except KeyboardInterrupt:
                print("Interrupted by user. Exiting.")
                sys.exit(0)

    def accept_and_respond(self):
        conn, addr = self.ssock.accept()
        print("Connected to {}:{}".format(addr[0], addr[1]))
        threading.Thread(target=self.client_thread, args=(conn, addr)).start()

    def client_thread(self, conn, addr):
        while True:
            # Client's mainloop
            data = conn.recv(1024).decode()
            if data == "exit":
                break
            if data == "":
                break
            conn.sendall((data[::-1]).encode())
            print("Received " + data)

        # Clean everything up
        conn.close()
        print("Thread exiting.")
        sys.exit(0)

if __name__ == '__main__':
    main()
