from base64 import decode
import socket
import select
import json
import sys

from json.decoder import JSONDecodeError
from unicodedata import name


def receive_message(client_socket):
    """Receive as many messages as specified by the first HEADER_LENGTH characters of the initial message and return all the data in JSON format

    :param [client_socket]: socket corresponding to the receiving client
    :type [client_socket]: socket.socket
    :rtype: dict
    """
    try:
        userData = ''   # function will return this JSON string
        new_message = True  # to distinguish the first message from the following messages
        while True:  # in this loop, the client keeps receiving messages until userData is as long as message_len
            temp = client_socket.recv(16).decode('utf-8')
            if (new_message):
                # message_len is communicated via the first HEADER_LENGTH characters of the first message
                message_len = int(temp[:HEADER_LENGTH].strip())
                # print(message_len)
                userData += temp[HEADER_LENGTH:]
                new_message = False
                continue

            userData += temp
            # print(len(userData))
            # print(userData)
            # print("USER: ",userData)

            # enough messages have been read
            if (message_len == len(userData)):
                userData = json.loads(userData)
                return userData

        # return {'Len':userData['userHeader'], 'Message':message}
    except JSONDecodeError as e:
        print(e)
        # Something went wrong like empty message or client exited abruptly.
        return False


if __name__ == '__main__':
    # message_len is communicated via the first HEADER_LENGTH characters of the first message
    HEADER_LENGTH = 10

    # get command line args
    IP = sys.argv[1]
    PORT = int(sys.argv[2])

    # initialize server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen()

    # we will be using only this one socket in this python file
    sockets_list = [server_socket]

    clients = {}
    print(f'Listening for connections on {IP}:{PORT}...')

    while True:
        # Of these three lists, returned by the selet method, 1st is the one which has all sockets whcih are ready to proceed.
        # 3rd is the one which throws some exception
        read_sockets, _, exception_sockets = select.select(
            sockets_list, [], sockets_list)

        for iter_socket in read_sockets:
            if iter_socket == server_socket:
                # accept new user
                client_socket, client_address = server_socket.accept()
                user = receive_message(client_socket)
                if not user:
                    continue
                sockets_list.append(client_socket)
                clients[client_socket] = user
                print('Accepted new connection from {}:{}, username: {}'.format(
                    *client_address, user['userMessage']))
            else:
                # receive a message from a registered user
                message = receive_message(iter_socket)
                if not message:
                    # empty message means graceful exit has already taken place
                    print('Closed connection from: {}'.format(
                        clients[iter_socket]))
                    sockets_list.remove(iter_socket)
                    # removes that particular socket from the clients dictionary
                    del clients[iter_socket]

                    continue

                # if message typed is exactly LEAVE GROUP the remove that client.(for which message should be true)
                if message:
                    if message['userMessage'] == "LEAVE GROUP":
                        print('Closed connection from: {}'.format(
                            clients[iter_socket]))
                        sockets_list.remove(iter_socket)
                        if message['userMessage'] == "LEAVE GROUP":
                            iter_socket.send("LEAVE".encode())
                        del clients[iter_socket]

                        continue

                user = clients[iter_socket]
                print(
                    f"Received message from {user['userMessage']}: {message['userMessage']}")

                for client_socket in clients:
                    # Send to all clients except the sender
                    if client_socket != iter_socket:

                        if (message['userMessage'] == "SEND IMAGE"):
                            message['userName'] = user['userMessage']
                            jsonData = json.dumps(message)
                            client_socket.send(
                                bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))
                            print("sent from server")
                            continue
                        # Send user and message (both with their headers)
                        # We are reusing here message header sent by sender, and saved username header send by user when he connected

                        message['userName'] = user['userMessage']
                        jsonData = json.dumps(message)
                        client_socket.send(
                            bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))

        # It's not really necessary to have this, but will handle some socket exceptions, just in case
        for notified_socket in exception_sockets:

            # Remove from list for socket.socket()
            sockets_list.remove(notified_socket)

            # Remove from our list of users
            del clients[notified_socket]
