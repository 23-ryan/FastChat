import socket
import sys
s = socket.socket()
port = 2234

s.connect(('127.0.0.12', port))
mess = ""
for i in range(1,len(sys.argv)):
    mess+=sys.argv[i]+" "
s.send(f"{mess}".encode())
print(s.recv(1024).decode('utf-8'))
s.close()
