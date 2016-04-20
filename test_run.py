import client
import server
import handler
import sys
import custom_logging
from time import time
from threading import Thread

def main():
    serv = server.Server("JRTI")
    serv.start()

    if len(sys.argv) < 1:
        NUM_MB_TO_SEND = 200
    else:
        NUM_MB_TO_SEND = int(sys.argv[1])
        custom_logging.logger.debug(NUM_MB_TO_SEND)
    lst = []
    t = time()
    for i in range(10):
        lst.append(client.Client(str(i)))

    for c in lst:
        c.send_sized_msg(("0123456789")*100000 * NUM_MB_TO_SEND) #1e6 bytes
    t = time() - t

    custom_logging.logger.debug(t)

if __name__ == '__main__':
    main()
