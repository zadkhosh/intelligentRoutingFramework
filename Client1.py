
mainPath = '/home/esi/mininetProject/networkFiles/'

import socket
import multiprocessing
import time

myfile = open(mainPath + 'data.zip', 'rb')
datafile = myfile.read()
def clientThread(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("10.0.0.2",port))
    while True:
        sock.sendall(datafile)

    sock.close()

cpuUsage = []

t0 = multiprocessing.Process(target=clientThread, args=(5050+0,))
t0.daemon = True
t0.start()
time.sleep(4)

t1 = multiprocessing.Process(target=clientThread, args=(5050+1,))
t1.daemon = True
t1.start()
time.sleep(4)

t2 = multiprocessing.Process(target=clientThread, args=(5050+2,))
t2.daemon = True
t2.start()
time.sleep(4)

t3 = multiprocessing.Process(target=clientThread, args=(5050+3,))
t3.daemon = True
t3.start()
time.sleep(4)
#
# t4 = multiprocessing.Process(target=clientThread, args=(5050+4,))
# t4.daemon = True
# t4.start()
time.sleep(30)
#
while(1):

    t0.terminate()
    time.sleep(1)
    t0 = multiprocessing.Process(target=clientThread, args=(5050+0,))
    t0.daemon = True
    t0.start()
    time.sleep(4)

    t1.terminate()
    time.sleep(1)
    t1 = multiprocessing.Process(target=clientThread, args=(5050+1,))
    t1.daemon = True
    t1.start()
    time.sleep(4)

    t2.terminate()
    time.sleep(1)
    t2 = multiprocessing.Process(target=clientThread, args=(5050+2,))
    t2.daemon = True
    t2.start()
    time.sleep(4)

    t3.terminate()
    time.sleep(1)
    t3 = multiprocessing.Process(target=clientThread, args=(5050+3,))
    t3.daemon = True
    t3.start()
    time.sleep(4)

    # t4.terminate()
    # time.sleep(1)
    # t4 = multiprocessing.Process(target=clientThread, args=(5050+4,))
    # t4.daemon = True
    # t4.start()
    time.sleep(30)
