# Most imortant note:
# DO CLOSE THE SOCKETS WHENEVER YOU OPEN THEM TO PREVENT RESOURCE LEAK!


from email import message
import socket
s = socket.socket()

port = 1234
# this socket instance will bind to a client with any ip address, but the clients port must be the same as 'port'
s.bind(('', port))

s.listen(10)  # maximum number of allowed connections
print(f"Listening on port {port}......")

# this list stores clients in the chronological order of their connection to the server
clients = []

# this loop makes the program wait till the socket instance s connects to two clients
while True:
    c, adrr = s.accept()
    clients.append(c)
    if (len(clients) == 2):
        break

# A is the client that connects first and B is the one who connects next
# the messages sent by A and B in chronological order
messageA = []
messageB = []


# following loop works properly only when the two clients send messages alternately. If either one sends a message out of his/her turn, the message will be stored in the list and sent eventually.
num = 0  # represents which client's turn it is to talk. 0 means A should be talking
while len(clients) != 0:
    if (num == 0):
        if (len(messageB) == 0):
            clients[0].send("==> No message yet <==".encode())
        else:
            clients[0].send(messageB[-1].encode())
        # recv is a blocking method. Therefore any messages sent by B in this timeframe will be stored in the list but not printed on A's terminal
        messageA.append(f"A:{clients[0].recv(1024).decode('utf-8')}")
        num = 1
    elif (num == 1):
        clients[1].send(messageA[-1].encode())
        # recv is a blocking method. Therefore any messages sent by A in this timeframe will be stored in the list but not printed on B's terminal
        messageB.append(f"B:{clients[1].recv(1024).decode('utf-8')}")
        num = 0


# HAVE TO FIX THIS (server socket must close.)
s.close()
