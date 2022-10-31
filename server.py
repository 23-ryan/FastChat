import socket
import select
import json

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 3000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))

server_socket.listen()

sockets_list = [server_socket]

clients = {}
print(f'Listening for connections on {IP}:{PORT}...')


def receive_message(client_socket):
    try:
        userData = client_socket.recv(1024)
        userData = json.loads(userData.decode('utf-8'))

        if not len(userData):
            return False

        message_length = int(userData['userHeader'].strip())
        message = userData['userMessage']
        if(message_length != len(message)):
            print("Complete message not recieved!")
        
        return {'Len':userData['userHeader'], 'Message':message}
    except:
        # Something went wrong like empty message or client exited abruptly.
        return False

while True:
    # Of these three lists, returned by the selet method, 1st is the one which has all sockets whcih are ready to proceed.
    # 3rd is the one which throws some exception
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for iter_socket in read_sockets:
            if iter_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                user = receive_message(client_socket)
                if not user:
                    continue
                sockets_list.append(client_socket)
                clients[client_socket] = user
                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['Message']))

            else:
                message = receive_message(iter_socket)
                if not message:
                    print('Closed connection from: {}'.format(clients[iter_socket]))
                    sockets_list.remove(iter_socket)
                    del clients[iter_socket] # removes that particular socket from the clients dictionary
                    
                    continue
                
                # if message typed is exactly LEAVE GROUP the remove that client.(for which message should be true)
                if message:
                    if message['Message'] == "LEAVE GROUP":
                        print('Closed connection from: {}'.format(clients[iter_socket]))
                        sockets_list.remove(iter_socket)
                        if message['Message'] == "LEAVE GROUP":
                            iter_socket.send("LEAVE".encode())
                        del clients[iter_socket]

                        continue


                user = clients[iter_socket]
                print(f"Received message from {user['Message']}: {message['Message']}")

                for client_socket in clients:
                    # But don't sent it to sender
                    if client_socket != iter_socket:
                        # Send user and message (both with their headers)
                        # We are reusing here message header sent by sender, and saved username header send by user when he connected
                        jsonData = json.dumps({"usernameLen":f"{user['Len'].strip()}" , "userName":f"{user['Message']}" , 'messageLen':f"{message['Len'].strip()}" , 'message':f"{message['Message']}"})
                        client_socket.send(bytes(jsonData, encoding='utf-8'))
                    

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]
