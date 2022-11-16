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

# function to connect to the database
def connectMydb(dbName):
    conn = psycopg2.connect(database =f"{dbName}", user = "postgres", password = "psql", host = "localhost", port = "5432")
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
        return False
    else:
        publicKey = proxy.getPublicKey(username)
        cur = connectMydb(MY_USERNAME)
        query = f'''INSERT INTO connections
                    VALUES('{username}', {publicKey[0]}, {publicKey[1]}, -1, -1, -1);'''
        cur.execute(query)
        query = f'''CREATE TABLE "{username}"(
                    person TEXT,
                    message TEXT);'''
        cur.execute(query)
    
    return True


def receive_message(client_socket):
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



if __name__ == '__main__':

    HEADER_LENGTH = 10

    IP = sys.argv[1]
    PORT = int(sys.argv[2])
    my_username = input("Username: ")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    username = my_username
    username_header = f"{len(username):<{HEADER_LENGTH}}"
    data = {'userHeader':f"{username_header}", 'userMessage':f"{username}"}
    jsonData = json.dumps(data)
    print(f'{len(jsonData):<10}')
    client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))

    sockets_list = [sys.stdin, client_socket]


    while True:
        try:
            read_sockets, _, error_sockets = select.select(sockets_list,[], sockets_list)
            for sockets in read_sockets:
                # LEAVE GROUP message
                if(client_socket == sockets):
                    data = receive_message(sockets)
                    # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                    if not data:
                        print('Connection closed by the server')
                        sys.exit()
                    
                    username = data['userName']
                    message = data['userMessage']

                    if message == "SEND IMAGE":
                        print(data)
                        ans = input("DO YOU WANT TO RECIEVE AN IMAGE SENT(YES/NO ?):")
                        if(ans.upper() == "YES"):
                            name = input("NAME OF IMAGE: ")
                            os.system(f'touch {name}.{data["imageFormat"]}')
                            with open(f'{name}.{data["imageFormat"]}', 'wb') as f:
                                f.write(base64.b64decode(data["imageData"]))
                                print('recieved Image')
                        continue

                    print(f'{username} > {message}')

                else:
                    message = sys.stdin.readline()[0:-1]
                    if message == "LEAVE GROUP":
                        jsonData = json.dumps({'userMessage':f"{message}"})
                        client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))
                        print("You are no longer a participant of this group")
                        sys.exit()

                    elif message == "SEND IMAGE":
                        path = input("PATH OF IMAGE: ")
                        img_json = ""
                        if(path != ""):
                            with open(path, 'rb') as f:
                                img_json = {'userMessage':f"{message}", 'imageFormat': f"{path.split('.')[-1]}", 'imageData':f"{base64.encodebytes(f.read()).decode('utf-8')}"}
                                print("Image sent")
                            jsonData = json.dumps(img_json)
                            client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))
            

                    elif message != "":
                        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
                        jsonData = json.dumps({'userMessage':f"{message}"})
                        client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))

                
        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data, error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error2: {}'.format(str(e)))
                sys.exit()
            # We just did not receive anything
            continue

        except Exception as e:
            # Any other exception - something happened, exit
            print('Reading error1: {}'.format(str(e)))
            sys.exit()