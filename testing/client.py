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

def isAdminOfGroup(grpName, MY_USERNAME):
    cur = connectMydb(MY_USERNAME)
    query = f'''SELECT isAdmin FROM connections WHERE username = '{grpName}';'''
    cur.execute(query)
    record = cur.fetchall()
    if(record == []):
        return False

    return record[0][0]

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
    # When message in a group is received the sender would be the person swending it ,
    # while according to the implementation we need to enter in table of sender/grpName
    grpName = sender
    if(data['isGroup']):
        grpName = data['grpName']
    if(not data['isGroup']):
        if(message=="REMOVE_PARTICIPANT"):
            grpName = data['grpName']

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

    if message == "ADD_PARTICIPANT":
        cur = connectMydb(MY_USERNAME)
        query = f'''CREATE TABLE "{data['grpName']}"(
                name TEXT,
                message TEXT);'''
        cur.execute(query)

        # #############################TODO################################ #
        # YOU MUST HAVE TO DECRYPT PRIVATE KEY USING THE PUBLIC KEY OF THIS USER
        # #############################TODO################################ #

        query = f'''INSERT INTO connections
                    VALUES('{data['grpName']}', {data['privateKey'][0]}, {data['privateKey'][1]}, {data['privateKey'][2]}, {data['privateKey'][3]}, {data['privateKey'][4]}, False)'''
        cur.execute(query)
        return True

    # if message == "REMOVE_PARTICIPANT":
    # NOT HERE , as we have to let user know that he is removed so drop table only when 
    # only when he opens the group
            
    # storing the data into the table corresponding to the sender
    query = f'''SELECT EXISTS (
            SELECT FROM
                pg_tables
            WHERE
                schemaname = 'public' AND
                tablename  = '{grpName}'
            )'''
    cur.execute(query)
    response = cur.fetchall()[0][0]
    # print(type(response))

    # If table already exists
    if(response):
        query = f'''INSERT INTO "{grpName}"
            VALUES('{sender}', '{message}')'''
        cur.execute(query)
        # print(colored(f'{decryptedMessage}', 'white', 'on_red'))

    else:
        addNewDM(MY_USERNAME, sender, proxy)
        query = f'''INSERT INTO "{sender}"
                    VALUES('{sender}', '{message}');'''
        cur.execute(query)
        # print(colored(f'{decryptedMessage}', 'white', 'on_red'))
    
    return (sender, grpName, decryptedMessage)


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

def getPrivateKey(group, sender):
    cur = connectMydb(sender)
    query = f'''SELECT publicn ,publice, privated, privatep, privateq from connections
                WHERE username = '{group}';'''
    cur.execute(query)
    record = cur.fetchall()[0]
    # print(record)
    # publicKey = rsa.key.PublicKey(record[0],record[1], record[2], record[3], record[4])
    return record

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
                    VALUES('{username}', {publicKey[0]}, {publicKey[1]}, -1, -1, -1, FALSE);'''
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

def createGroup(grpName, ADMIN, proxy):
    cur = connectMydb(ADMIN)
    ###########################
    publicKey, privateKey = rsa.newkeys(30)
                                
    query = f'''INSERT INTO connections
            VALUES('{grpName}',{publicKey['n']}, {publicKey['e']}, {privateKey['d']}, {privateKey['p']}, {privateKey['q']}, TRUE)'''

    cur.execute(query)
    ###########################
    proxy.createGroupAtServer(grpName, ADMIN)

    query = f'''CREATE TABLE "{grpName}"(
                name TEXT,
                message TEXT);'''
    cur.execute(query)

################ TODO ####################
# Recieve ack from client , try doing for messages when receiver is active too!
##########################################
# IDEA - what we can do is that check the ack_text = socket.recv() ,
# now if it is that message has been recieved then send a confiramtion to 
# server as a message through client and once that is done only then allow the 
# server to move ahead , set a timeout and if ack is not received in that time
# store the message as pending messages and continue with the loop
##########################################
# Pointer to last read messages so the rest are printed when the user opens the interface
# Online-Offline status updation and storing-sending messages accordingly
# ENCRYPTION
# Multi-server load balancing
################ TODO ####################