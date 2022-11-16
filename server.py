# "" are used to make table names case insensitive

from base64 import decode
import socket
import select
import json
import sys

from termcolor import colored
from serverDatabase import connectToDb
from json.decoder import JSONDecodeError

import xmlrpc.server as Server

class MyServer(Server.SimpleXMLRPCServer):

    def serve_forever(self):
        self.quit = 0
        while not self.quit:
            self.handle_request()

def  getPublicKey(username):
    cur = connectToDb()
    query = f'''SELECT publicn, publice FROM userinfo WHERE username='{username}';'''
    cur.execute(query)
    record = cur.fetchall()[0]
    print(record)
    return record
    # return (password == recordPassword)
    

def isValidPassword(userName, password):
    cur = connectToDb()
    query = f'''SELECT password FROM userinfo WHERE username='{userName}';'''
    cur.execute(query)
    recordPassword = cur.fetchall()[0][0]
    return (password == recordPassword)

def checkUserName(userName):
    print("hehe")
    cur = connectToDb()
    print("hi")
    query = f'''SELECT username FROM userinfo;'''
    cur.execute(query)
    print("hoho")
    record = cur.fetchall()
    print(record)
    return (f"{userName}",) in record


def addNewUser(userName,password, n, e):
    cur = connectToDb()
    print("hi")
    query = f'''INSERT INTO userinfo
                VALUES ('{userName}', '{password}', {int(n)}, {int(e)});'''
    print("hehe")
    print(userName)
    cur.execute(query)
    cur.execute("SELECT * FROM userinfo")
    print(cur.fetchall())
    print("ksndksnd")

def receive_message(client_socket):
    try:
        userData = ''
        new_message = True
        while True:
            temp = client_socket.recv(16).decode('utf-8')
            if(new_message):
                print(temp)
                message_len = int(temp[:HEADER_LENGTH].strip())
                userData += temp[HEADER_LENGTH:]
                new_message = False
                continue
            
            userData += temp
            # print("USER: ",userData)
            if(message_len == len(userData)):
                userData = json.loads(userData)
                return userData


        # return {'Len':userData['userHeader'], 'Message':message}
    except JSONDecodeError as e:
        print(e)
        # Something went wrong like empty message or client exited abruptly.
        return False


if __name__ == '__main__':

    HEADER_LENGTH = 10

    IP = sys.argv[1]
    PORT = int(sys.argv[2])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))

    server_socket.listen()

    sockets_list = [server_socket]

    clients = {}
    print(f'Listening for connections on {IP}:{PORT}...')

    # NEW XMLRPC SERVER
    rpcServer = MyServer((IP, 3000), logRequests=False,allow_none=True)
    rpcServer.register_function(isValidPassword)
    rpcServer.register_function(addNewUser)
    rpcServer.register_function(checkUserName)
    rpcServer.register_function(getPublicKey)
    rpcServer.serve_forever()

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
                    print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['userMessage']))

                else:
                    message = receive_message(iter_socket)
                    if not message:
                        print('Closed connection from: {}'.format(clients[iter_socket]))
                        sockets_list.remove(iter_socket)
                        del clients[iter_socket] # removes that particular socket from the clients dictionary
                        
                        continue

                    # if message typed is exactly LEAVE GROUP the remove that client.(for which message should be true)
                    if message:
                        if message['userMessage'] == "LEAVE GROUP":
                            print('Closed connection from: {}'.format(clients[iter_socket]))
                            sockets_list.remove(iter_socket)
                            if message['userMessage'] == "LEAVE GROUP":
                                iter_socket.send("LEAVE".encode())
                            del clients[iter_socket]

                            continue


                    user = clients[iter_socket]
                    print(f"Received message from {user['userMessage']}: {message['userMessage']}")

                    for client_socket in clients:
                        # But don't sent it to sender
                        if client_socket != iter_socket:

                            if(message['userMessage'] == "SEND IMAGE"):
                                message['userName'] = user['userMessage']
                                jsonData = json.dumps(message)
                                client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))
                                print("sent from server")
                                continue
                            # Send user and message (both with their headers)
                            # We are reusing here message header sent by sender, and saved username header send by user when he connected

                            message['userName'] = user['userMessage']
                            jsonData = json.dumps(message)
                            client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))
                        

        # It's not really necessary to have this, but will handle some socket exceptions just in case
        for notified_socket in exception_sockets:

            # Remove from list for socket.socket()
            sockets_list.remove(notified_socket)

            # Remove from our list of users
            del clients[notified_socket]