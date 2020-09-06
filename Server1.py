import socket
import sys
import threading
import time

troughtput = 0
timeIdx = 0


def serverThread(port):
    global troughtput
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("10.0.0.2",port))
    sock.listen(10)
    t = time.clock()
    while True:
        con, client_addr = sock.accept()
        while True:
            data = con.recv(1000000000)
            if not(data):
                break
        con.close()

for i in range(int(4)):
    t = threading.Thread(target=serverThread, args=(5050+i,))
    t.daemon = True
    t.start()
    time.sleep(0.1)


while True:
    time.sleep(3600/60)
