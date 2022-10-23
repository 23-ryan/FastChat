import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))

server_socket.listen()

sockets_list = [server_socket]

clients = {}
print(f'Listening for connections on {IP}:{PORT}...')


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())

        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:
        # Something went wrong like empty message or client exited abruptly.
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for new_socket in read_sockets:
            if new_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                user = receive_message(client_socket)
                if not user:
                    continue
                sockets_list.append(client_socket)
                clients[client_socket] = user
                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

            else:
                message = receive_message(new_socket)
                # print("---------------", message)
                if not message or message['data'].decode('utf-8') == "LEAVE GROUP":
                    print('Closed connection from: {}'.format(clients[new_socket]['data'].decode('utf-8')))
                    sockets_list.remove(new_socket)
                    
                    if message['data'].decode('utf-8') == "LEAVE GROUP":
                        new_socket.send("LEAVE".encode())
                    del clients[new_socket]
                    
                    continue
                
                user = clients[new_socket]
                print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

                for client_socket in clients:
                    # But don't sent it to sender
                    if client_socket != new_socket:
                        # Send user and message (both with their headers)
                        # We are reusing here message header sent by sender, and saved username header send by user when he connected
                        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                    


    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]
