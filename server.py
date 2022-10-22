# Most imortant note:
# DO CLOSE THE SOCKETS WHENEVER YOU OPENS THEM ! ELSE YOU WOULD RUN OUT OF THEM FOR SOME TIME!

 
from email import message
import socket
s = socket.socket()

port = 1234
s.bind(('', port)) # 

s.listen(10) # maximum number of allowed connections
print(f"Listening on port{port}......")


clients = []

while True:
    c, adrr = s.accept()
    clients.append(c)
    if(len(clients) == 2):
        break

messageA = []
messageB = []

num = 0
while len(clients)!=0:
    if(num == 0):
        if(len(messageB) == 0):
            clients[num].send("==> No message yet <==".encode())
        else:
            clients[num].send(messageB[-1].encode())
        messageA.append(f"B:{clients[num].recv(1024).decode('utf-8')}")
        num = (num+1)%2
    elif(num == 1):
        clients[num].send(messageA[-1].encode())
        messageB.append(f"A:{clients[num].recv(1024).decode('utf-8')}")
        num = (num+1)%2



# HAVE TO FIX THIS (server sockt must close.)
s.close()

