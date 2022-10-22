import socket
s = socket.socket()

port = 1234
s.connect(('localhost', port))
mess = ""

# receive a message from the server (written by the other client)
incomMess = s.recv(1024)

# funnily, if the other client types quit, this client's connection will close
while incomMess != "quit":
    print(incomMess.decode())
    a = input()
    s.send(a.encode())
    incomMess = s.recv(1024)

s.close()
