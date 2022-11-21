import os
import socket
import select
import errno
import sys
import rsa
import json
import base64
from client import receive_message, getPublicKey, unpack_message
from termcolor import colored
from client import connectMydb


def handleDM(MY_USERNAME, OTHER_USERNAME, client_socket, proxy, isGroup):

        sockets_list = [sys.stdin, client_socket]

        while True:
            try:
                read_sockets, _, error_sockets = select.select(sockets_list,[], sockets_list)
                for sockets in read_sockets:
                    # LEAVE GROUP message
                    if(client_socket == sockets):
                        data = unpack_message(sockets)
                        data = receive_message(data, proxy)

                        if(data and data[1] == OTHER_USERNAME and data[2]=="REMOVE_PARTICIPANT"):
                            cur = connectMydb(MY_USERNAME)
                            query = f'''DROP TABLE "{OTHER_USERNAME}";'''
                            cur.execute(query)
                            query = f'''DELETE FROM connections WHERE username = '{OTHER_USERNAME}';'''
                            cur.execute(query)
                            print(colored("YOU WERE KICKED FROM THE GROUP!", 'yellow'))
                        # DON'T PRINT THE MESSAGE OF OTHER USER IN ONE'S TERMINAL
                        elif(data and data[1] == OTHER_USERNAME):
                            print(f"{data[0]} > ", colored(f'{data[2]}', 'white', 'on_red'))
                        # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)

                    else:
                        print("sdsds")
                        print("-------")
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
                                    img_json = {'userMessage':f"{message}", 'sender':f"{MY_USERNAME}" , 'receiver':f"{OTHER_USERNAME}",  'imageFormat': f"{path.split('.')[-1]}", 'imageData':f"{base64.encodebytes(f.read()).decode('utf-8')}", 'isGroup':isGroup}
                                    print("Image sent")
                                jsonData = json.dumps(img_json)
                                client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))
                

                        elif message != "":
                            # print("HERE")
                            publicKey = getPublicKey(OTHER_USERNAME, MY_USERNAME)
                            print(publicKey)
                            # print(type(message))
                            # message = rsa.encrypt(message.encode('utf-8'),publicKey)
                            print(message)

                            # INSERT data into the table
                            cur = connectMydb(MY_USERNAME)
                            query = f'''INSERT INTO "{OTHER_USERNAME}"
                                    VALUES('{MY_USERNAME}', '{message}')'''
                            cur.execute(query)
                            print("ksdks")
                            
                            # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
                            jsonData = json.dumps({'userMessage':f"{message}",'sender':f"{MY_USERNAME}", 'receiver':f"{OTHER_USERNAME}", 'isGroup':isGroup})
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
