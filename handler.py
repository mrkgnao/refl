import threading
from threading import Thread

class Handler(Thread):
    """A Handler is an object that communicates with a client."""
    def __init__(self, client):
        self.client = client

    def start(self):
        self.client.sendall("Harro from handler bby")
