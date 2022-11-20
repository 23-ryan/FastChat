
import os
import socket
import select
import errno
import sys
import json
import base64
from json.decoder import JSONDecodeError
from termcolor import colored
import psycopg2
import rsa

HEADER_LENGTH = 10

# function to connect to the database

def decryptMessage(message, cur, MY_USERNAME):
    query =f'''SELECT publicn,publice,privated,privatep,privateq FROM
                userinfo WHERE username = {MY_USERNAME};'''
    cur.execute(query)
    components = cur.fetchall()[0]
    PrivateKey = rsa.key.PrivateKey(components[0],components[1],components[2],components[3],components[4])
    # check if has been already decoded or not
    decryptedMessage = rsa.decrypt(message,PrivateKey).decode()
    return decryptedMessage

def receive_message(data, proxy):
    if not data:
        print('Connection closed by the server')
        return None
    print(data)
    sender = data['sender']
    MY_USERNAME = data['receiver']
    message = data['userMessage']

    cur = connectMydb(MY_USERNAME)
    # decryptedMessage = decryptMessage(message, cur, MY_USERNAME)
    decryptedMessage = message

    if message == "SEND IMAGE":
        # print(data)
        ans = input("DO YOU WANT TO RECIEVE AN IMAGE SENT(YES/NO ?):")
        if(ans.upper() == "YES"):
            name = input("NAME OF IMAGE: ")
            os.system(f'touch {name}.{data["imageFormat"]}')
            with open(f'{name}.{data["imageFormat"]}', 'wb') as f:
                f.write(base64.b64decode(data["imageData"]))
                print('recieved Image')

    # storing the data into the table corresponding to the sender
    query = f'''SELECT EXISTS (
            SELECT FROM
                pg_tables
            WHERE
                schemaname = 'public' AND
                tablename  = '{sender}'
            )'''
    cur.execute(query)
    response = cur.fetchall()[0][0]
    # print(type(response))

    # If table already exists
    if(response):
        query = f'''INSERT INTO "{sender}"
            VALUES('{sender}', '{message}')'''
        cur.execute(query)
        # print(colored(f'{decryptedMessage}', 'white', 'on_red'))

    else:
        addNewDM(MY_USERNAME, sender, proxy)
        query = f'''INSERT INTO "{sender}"
                    VALUES('{sender}', '{message}');'''
        cur.execute(query)
        # print(colored(f'{decryptedMessage}', 'white', 'on_red'))
    
    return (sender, decryptedMessage)


def checkSocketReady(socket):
    print("hello")
    read_sockets, _, error_sockets = select.select([socket],[], [socket], 0.01)
    if read_sockets != []:
        return read_sockets[0]
    else:
        return False
        
        

def getPublicKey(reciever, sender):
    cur = connectMydb(sender)
    query = f'''SELECT publicn ,publice from connections
                WHERE username = '{reciever}';'''
    cur.execute(query)
    record = cur.fetchall()[0]
    # print(record)
    publicKey = rsa.key.PublicKey(record[0],record[1])
    return publicKey

def goOnline(username, IP, PORT):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    username_header = f"{len(username):<{HEADER_LENGTH}}"
    data = {'userHeader':f"{username_header}", 'userMessage':f"{username}"}
    jsonData = json.dumps(data)
    print(f'{len(jsonData):<10}')
    client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))

    return client_socket

def connectMydb(dbName):
    conn = psycopg2.connect(database =f"{dbName}", user = "postgres", password = "postgres", host = "localhost", port = "5432")
    conn.autocommit = True
    cur = conn.cursor()
    return cur

# check the availability in connections table
def isInConnections(MY_USERNAME, username):
    cur = connectMydb(MY_USERNAME)
    query = f'''SELECT username FROM connections;'''
    cur.execute(query)
    record = cur.fetchall()

    return ((f"{username}",) in record)


# returns lists of all the users and groups to get listed
def getAllUsers(MY_USERNAME):
    DM = []
    group = [] 
    
    cur = connectMydb(MY_USERNAME)
    query = f'''SELECT username FROM connections WHERE privated = -1;'''
    cur.execute(query)
    record = cur.fetchall()
    for i in record:
        DM.append(i[0])

    query = f'''SELECT username FROM connections WHERE privated != -1;'''
    cur.execute(query)
    record = cur.fetchall()
    for i in record:
        group.append(i[0])

    return DM, group


#  Adding a new DM as requested by the user
def addNewDM(MY_USERNAME, username, proxy):
    # checking that the user is registered with the app or not
    if(not proxy.checkUserName(username)):
        print("HELLO")
        return False
    else:
        publicKey = proxy.getPublicKey(username)
        print("HELLO")
        cur = connectMydb(MY_USERNAME)
        query = f'''INSERT INTO connections
                    VALUES('{username}', {publicKey[0]}, {publicKey[1]}, -1, -1, -1);'''
        cur.execute(query)

        query = f'''SELECT EXISTS (
            SELECT FROM
                pg_tables
            WHERE
                schemaname = 'public' AND
                tablename  = '{username}'
            )'''
        cur.execute(query)
        response = cur.fetchall()[0][0]

        if(not response):
            query = f'''CREATE TABLE "{username}"(
                        person TEXT,
                        message TEXT);'''
            cur.execute(query)
    
    return True


def unpack_message(client_socket):
    try:
        userData = ''
        new_message = True
        while True:
            temp = client_socket.recv(16).decode('utf-8')
            if(temp == ""):
                return
            if(new_message):
                message_len = int(temp[:HEADER_LENGTH].strip())
                # print(message_len)
                userData += temp[HEADER_LENGTH:]
                new_message = False
                continue
            
            userData += temp
            # print(len(userData))
            # print(userData)
            # print("USER: ",userData)
            if(message_len == len(userData)):
                userData = json.loads(userData)
                return userData


        # return {'Len':userData['userHeader'], 'Message':message}
    except JSONDecodeError as e:
        print(e)
        # Something went wrong like empty message or client exited abruptly.
        return False



# if __name__ == '__main__':

#     HEADER_LENGTH = 10

#     IP = sys.argv[1]
#     PORT = int(sys.argv[2])
#     my_username = input("Username: ")

#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#     client_socket.connect((IP, PORT))
#     client_socket.setblocking(False)
#     username = my_username
#     username_header = f"{len(username):<{HEADER_LENGTH}}"
#     data = {'userHeader':f"{username_header}", 'userMessage':f"{username}"}
#     jsonData = json.dumps(data)
#     print(f'{len(jsonData):<10}')
#     client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))

#     sockets_list = [sys.stdin, client_socket]


#     while True:
#         try:
#             read_sockets, _, error_sockets = select.select(sockets_list,[], sockets_list)
#             for sockets in read_sockets:
#                 # LEAVE GROUP message
#                 if(client_socket == sockets):
#                     data = unpack_message(sockets)
#                     # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
#                     recieve_message(data)

#                 else:
#                     message = sys.stdin.readline()[0:-1]
#                     if message == "LEAVE GROUP":
#                         jsonData = json.dumps({'userMessage':f"{message}"})
#                         client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))
#                         print("You are no longer a participant of this group")
#                         sys.exit()

#                     elif message == "SEND IMAGE":
#                         path = input("PATH OF IMAGE: ")
#                         img_json = ""
#                         if(path != ""):
#                             with open(path, 'rb') as f:
#                                 img_json = {'userMessage':f"{message}", 'imageFormat': f"{path.split('.')[-1]}", 'imageData':f"{base64.encodebytes(f.read()).decode('utf-8')}"}
#                                 print("Image sent")
#                             jsonData = json.dumps(img_json)
#                             client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))
            

#                     elif message != "":
#                         # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
#                         jsonData = json.dumps({'userMessage':f"{message}"})
#                         client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))

                
#         except IOError as e:
#             # This is normal on non blocking connections - when there are no incoming data, error is going to be raised
#             # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
#             # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
#             # If we got different error code - something happened
#             if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
#                 print('Reading error2: {}'.format(str(e)))
#                 sys.exit()
#             # We just did not receive anything
#             continue

#         except Exception as e:
#             # Any other exception - something happened, exit
#             print('Reading error1: {}'.format(str(e)))
#             sys.exit()