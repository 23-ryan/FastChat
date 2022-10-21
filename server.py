# Most imortant note:
# DO CLOSE THE SOCKETS WHENEVER YOU OPENS THEM ! ELSE YOU WOULD RUN OUT OF THEM FOR SOME TIME!

 
import socket
s = socket.socket()

messages = []

def handleClient(client):
    c, adrr = client
    mess = c.recv(1024).decode('utf-8')
    if(len(messages) != 0):
        c.send(f"You friend says:  {messages[-1]}".encode())
    messages.append(mess)
    c.close()

port = 2234
s.bind(('', port))

s.listen(10) # maximum number of allowed connections
print(f"Listening on port{port}......")

while True:
    handleClient(s.accept())

# HAVE TO FIX THIS (server sockt must close.)
s.close()

