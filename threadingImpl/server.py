import socket
import this
import threading  # Libraries import


host = '127.0.0.1'  # LocalHost
port = 4000  # Choosing unreserved port

# socket initialization
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))  # binding host and port to socket
server.listen()

clients = []
nicknames = []



def kick(client):
    client.send('YOU ARE BEING KICKED'.encode('utf-8'))
    index = clients.index(client)
    clients.remove(client)
    print(clients)
    del client
    nickname = nicknames[index]
    broadcast('{} left!'.format(nickname).encode('utf-8'))
    nicknames.remove(nickname)


def broadcast(message):  # broadcast function declaration
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        index = clients.index(client)
        message = client.recv(1024)

        # if the client types 'LEAVE GROUP' as his/her message
        # Used a try and except block that tries to provide some time for the current thread to sync with other thread changes
        try:
            if message.decode('utf-8') == '{}: LEAVE GROUP'.format(nicknames[index]):
                kick(client)
                break
            else:
                broadcast(message)
        except:
            continue

def receive():  # accepting multiple clients
    while True:
        client, address = server.accept()
        print("Connected with {}".format(str(address)))
        client.send('NICKNAME'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)
        print("Nickname is {}".format(nickname))
        broadcast("{} joined!".format(nickname).encode('utf-8'))
        client.send('Connected to server!'.encode('utf-8'))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


receive()
