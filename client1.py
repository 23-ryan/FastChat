import socket
s = socket.socket()

port = 1234
s.connect(('localhost', port))
mess = ""

incomMess = s.recv(1024)
while incomMess!="quit":
    print(incomMess.decode())
    a = input()
    s.send(a.encode())
    incomMess = s.recv(1024)

s.close()