import socket
import threading
import sys
import random
import load_config

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = load_config.get_server_port() #random.randrange(2000, 40000)
s.bind(('127.0.0.1', port))
s.listen(10)

print("Ready to handle connections on port {}".format(port))

def client_thread(conn):
    conn.sendall("Welcome.".encode())
    while True: #mainloop
        data = conn.recv(1024).decode()
        if data == "exit":
            break
        if data == "":
            break
        conn.sendall((data[::-1]).encode())
        print("Received " + data)
    conn.close()
    print("Thread exiting.")
    sys.exit(0)

while True:
    conn, addr = s.accept()
    print("Connected to {}:{}".format(addr[0], addr[1]))
    threading._start_new_thread(client_thread, (conn, ))
