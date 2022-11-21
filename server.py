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
    query = f'''SELECT password = crypt('{password}', password) FROM userinfo WHERE username='{userName}';'''
    cur.execute(query)
    recordPassword = cur.fetchall()
    return recordPassword[0][0]

def checkUserName(userName):
    cur = connectToDb()    
    query = f'''SELECT username FROM userinfo'''
    cur.execute(query)
    record = cur.fetchall()
    return (f"{userName}",) in record


def addNewUser(userName,password, n, e):
    cur = connectToDb()
    print("hi")
    # --------------------------
    # CREATE EXTENSION pgcrypto;
    # --------------------------
    query = f'''INSERT INTO userinfo
                VALUES ('{userName}', crypt('{password}', gen_salt('bf', 8)), {int(n)}, {int(e)});'''
    print("hehe")
    print(userName)
    cur.execute(query)
    cur.execute("SELECT * FROM userinfo")
    print(cur.fetchall())
    print("ksndksnd")

def unpack_message(client_socket):
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

# extracts the scket corresponding to a particular username
def getSocket(reciever, clients):
    return list(clients.keys())[list(clients.values()).index(reciever)]

# def fetchUsersInGroup(groupName):

def createGroupAtServer(grpName, ADMIN):
    cur = connectToDb()
    query = f'''CREATE TABLE "{grpName}"(
                name TEXT);'''
    cur.execute(query)

    # public key = -1 TO identify a group into userinfo table #
    query = f'''INSERT INTO userinfo
                VALUES('{grpName}', '', -1, -1)'''
    cur.execute(query)
    
    query = f'''INSERT INTO "{grpName}"
                VALUES('{ADMIN}')'''
    cur.execute(query)

def addUserToGroup(grpName, newuser):
    cur = connectToDb()
    query = f'''INSERT INTO "{grpName}"
                VALUES('{newuser}');'''
    cur.execute(query)


def getUsersList(grpName):
    cur = connectToDb()
    query = f'''SELECT name FROM "{grpName}"'''
    cur.execute(query)
    record = cur.fetchall()
    usersList = [i[0] for i in record]
    return usersList


def initialize():
    cur = connectToDb()
    lis = ['pending', 'userinfo']
    for table in lis:
        query = f'''SELECT EXISTS (
                SELECT FROM
                    pg_tables
                WHERE
                    schemaname = 'public' AND
                    tablename  = '{table}'
                )'''
        cur.execute(query)
        response = cur.fetchall()[0][0]
        if(not response):
            if(table == 'userinfo'):
                query = f'''CREATE TABLE userinfo(
                            username TEXT,
                            password TEXT,
                            publicn BIGINT,
                            publice BIGINT);'''
                cur.execute(query)
            elif(table == 'pending'):
                query = f'''CREATE TABLE pending(
                            sender TEXT,
                            receiver TEXT,
                            grpName TEXT,
                            message TEXT);'''
                cur.execute(query)

def handlePendingMessages(client_socket):
    receiverName = clients[client_socket]
    cur = connectToDb()
    query = f'''SELECT * FROM pending WHERE receiver = '{receiverName}';'''
    cur.execute(query)
    record = cur.fetchall()
    for rec in record:
        print("------------------GAYA_-------")
        isGroup = True
        if(rec[2] == ""):
            isGroup = False
        message = {'sender':f"{rec[0]}", 'receiver':f"{rec[1]}", 'grpName':f"{rec[2]}", 'userMessage':f"{rec[3]}", 'isGroup':isGroup}
        jsonData = json.dumps(message)
        client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))

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
    rpcServer = MyServer((IP, 3000), logRequests=False, allow_none=True)
    rpcServer.register_function(isValidPassword)
    rpcServer.register_function(addNewUser)
    rpcServer.register_function(checkUserName)
    rpcServer.register_function(getPublicKey)
    rpcServer.register_function(createGroupAtServer)
    # rpcServer.serve_forever()
    rpcServer.server_activate()

    initialize()
    while True:
        # Of these three lists, returned by the selet method, 1st is the one which has all sockets whcih are ready to proceed.
        # 3rd is the one which throws some exception
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        for iter_socket in read_sockets:
                if iter_socket == server_socket:
                    client_socket, client_address = server_socket.accept()
                    user = unpack_message(client_socket)
                    if not user:
                        continue
                    sockets_list.append(client_socket)
                    clients[client_socket] = user
                    handlePendingMessages(client_socket)
                    print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['userMessage']))

                else:
                    message = unpack_message(iter_socket)
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
                    if(not message['isGroup']):
                        # message['userName'] = user['userMessage'] # sender name
                        jsonData = json.dumps(message)
                        sock = getSocket(message['receiver'], clients)
                        sock.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))

                        if not message['receiver'] in list(clients.values()):
                            cur = connectToDb()
                            query = f'''INSERT INTO pending
                                        VALUES('{message['sender']}', '{message['receiver']}', '', '{message['userMessage']}');'''
                            cur.execute(query)

                
                    elif(message['isGroup']):
                        usersList = getUsersList(message['receiver'])
                        message['grpName'] = message['receiver']
                        for client_socket in clients:
                            # But don't sent it to sender
                            if client_socket != iter_socket and (clients[client_socket] in usersList):
                                message['receiver'] = clients[client_socket]
                                
                                # Send user and message (both with their headers)
                                # We are reusing here message header sent by sender, and saved username header send by user when he connected

                                jsonData = json.dumps(message)
                                client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))
                        
                        for groupMem in usersList:
                            message['receiver'] = groupMem
                            if(not groupMem in list(clients.values())):
                                cur = connectToDb()
                                query = f'''INSERT INTO pending
                                            VALUES('{message['sender']}', '{message['receiver']}', '{message['grpName']}', '{message['userMessage']}');'''
                                cur.execute(query)

        # It's not really necessary to have this, but will handle some socket exceptions just in case
        print(exception_sockets)
        for notified_socket in exception_sockets:
            # print(notified_socket)
            # Remove from list for socket.socket()
            sockets_list.remove(notified_socket)

            # Remove from our list of users
            del clients[notified_socket]