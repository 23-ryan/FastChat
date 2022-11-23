import os
import socket
import select
import errno
import sys
import rsa
import json
import base64
from client import receive_message, getPublicKey, unpack_message, sendAck
from termcolor import colored
from client import connectMydb


def handleDM(MY_USERNAME, OTHER_USERNAME, client_socket, proxy, isGroup):
    """To be used when MY_USERNAME sends a message to OTHER_USERNAME.
    Handles the keywords REMOVE_PARTICIPANT, LEAVE GROUP, and SEND IMAGE.

    :param [MY_USERNAME]: username of the client who sent DM
    :type [MY_USERNAME]: str
    :param [OTHER_USERNAME]: username of the receiving client/group
    :type [OTHER_USERNAME]: str
    :param [client_socket]: username of the receiving client/group
    :type [client_socket]: str
    :param [proxy]: proxy server for remote call to receive_message
    :type [proxy]: ServerProxy
    :param [isGroup]: whether the receiver is a group
    :type [isGroup]: bool
    """
    cur = connectMydb(MY_USERNAME)
    query = f'''SELECT readUpto FROM connections WHERE username = '{OTHER_USERNAME}';'''
    cur.execute(query)
    readUpto = cur.fetchall()[0][0]
    query = f'''SELECT * FROM "{OTHER_USERNAME}" WHERE messageId > {readUpto}'''
    cur.execute(query)
    record = cur.fetchall()

    isImage = False
    finalMessageId = 0
    for rec in record:
        if (isImage):
            ans = input("DO YOU WANT TO RECIEVE AN IMAGE SENT(YES/NO ?):")
            if (ans.upper() == "YES"):
                name = input("SAVE IMAGE AS: ")
                os.system(f'touch {name}.{rec[0]}')
                with open(f'{name}.{rec[0]}', 'wb') as f:
                    f.write(base64.b64decode(rec[1]))
                    print(colored('RECEIVED IMAGE!!', 'green'))
            isImage = False

        elif (rec[1] == "SEND IMAGE"):
            isImage = True

        elif (rec[1] == "REMOVE_PARTICIPANT"):
            query = f'''DROP TABLE "{OTHER_USERNAME}";'''
            cur.execute(query)
            query = f'''DELETE FROM connections WHERE username = '{OTHER_USERNAME}';'''
            cur.execute(query)
            print(colored("YOU WERE KICKED FROM THE GROUP!", 'yellow'))

        else:
            print(f"{rec[0]} > ", colored(f'{rec[1]}', 'white', 'on_red'))

        finalMessageId = rec[2]

    if (finalMessageId != 0):
        query = f'''UPDATE connections SET readUpto = {finalMessageId} WHERE username = '{OTHER_USERNAME}';'''
        cur.execute(query)

    sockets_list = [sys.stdin, client_socket]

    while True:
        try:
            read_sockets, _, error_sockets = select.select(
                sockets_list, [], sockets_list)
            for sockets in read_sockets:
                # LEAVE GROUP message
                if (client_socket == sockets):
                    data = unpack_message(sockets)
                    data = receive_message(data, proxy)

                    sendAck(client_socket, data[3], data[4])

                    if (data and data[1] == OTHER_USERNAME and data[2] == "REMOVE_PARTICIPANT"):
                        cur = connectMydb(MY_USERNAME)
                        query = f'''DROP TABLE "{OTHER_USERNAME}";'''
                        cur.execute(query)
                        query = f'''DELETE FROM connections WHERE username = '{OTHER_USERNAME}';'''
                        cur.execute(query)
                        print(colored("YOU WERE KICKED FROM THE GROUP!", 'yellow'))
                    # DON'T PRINT THE MESSAGE OF OTHER USER IN ONE'S TERMINAL

                    elif (data and data[1] == OTHER_USERNAME and data[2] == "SEND IMAGE"):
                        ans = input(
                            "DO YOU WANT TO RECIEVE AN IMAGE SENT(YES/NO ?):")
                        if (ans.upper() == "YES"):
                            name = input("SAVE IMAGE AS: ")
                            os.system(f'touch {name}.{data[5]}')
                            with open(f'{name}.{data[5]}', 'wb') as f:
                                f.write(base64.b64decode(data[6]))
                                print('recieved Image')

                    elif (data and data[1] == OTHER_USERNAME):
                        print(f"{data[0]} > ", colored(
                            f'{data[2]}', 'white', 'on_red'))

                    query = f'''SELECT MAX(messageId) FROM "{OTHER_USERNAME}";'''
                    cur.execute(query)
                    maxId = cur.fetchall()[0][0]
                    query = f'''UPDATE connections SET readUpto = {maxId} WHERE username = '{OTHER_USERNAME}';'''
                    cur.execute(query)
                    
                    # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)

                else:
                    # print("sdsds")
                    print("-------")
                    message = sys.stdin.readline()[0:-1]
                    if message == "LEAVE GROUP":
                        jsonData = json.dumps(
                            {'userMessage': f"{message}", 'isAck': False})
                        client_socket.send(
                            bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))
                        print("You are no longer a participant of this group")
                        sys.exit()

                    elif message == "SEND IMAGE":
                        path = input("PATH OF IMAGE: ")
                        img_json = ""
                        if (path != ""):
                            with open(path, 'rb') as f:
                                img_json = {'userMessage': f"{message}", 'sender': f"{MY_USERNAME}", 'receiver': f"{OTHER_USERNAME}",
                                            'imageFormat': f"{path.split('.')[-1]}", 'imageData': f"{base64.encodebytes(f.read()).decode('utf-8')}", 'isGroup': isGroup, 'isAck': False}
                                print("Image sent")
                            jsonData = json.dumps(img_json)
                            client_socket.send(
                                bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))
                            
                            query = f'''SELECT COALESCE(MAX(messageId), 0) FROM "{OTHER_USERNAME}";'''
                            cur.execute(query)
                            record = cur.fetchall()
                            nextRowNum = record[0][0] + 1

                            query = f'''INSERT INTO "{OTHER_USERNAME}" 
                                        VALUES ('{MY_USERNAME}','{message}', {nextRowNum});'''
                            cur.execute(query)
                            query = f'''INSERT INTO "{OTHER_USERNAME}"
                                        VALUES ('{img_json["imageFormat"]}', '{img_json["imageData"]}', {nextRowNum + 1});'''
                            cur.execute(query)

                            query = f'''UPDATE connections SET readUpto = {nextRowNum + 1} WHERE username = '{OTHER_USERNAME}';'''
                            cur.execute(query)

                    elif message != "":
                        # print("HERE")
                        publicKey = getPublicKey(OTHER_USERNAME, MY_USERNAME)
                        # print(publicKey)
                        # print(type(message))
                        # message = rsa.encrypt(message.encode('utf-8'),publicKey)
                        # print(message)

                        # INSERT data into the table
                        cur = connectMydb(MY_USERNAME)
                        query = f'''SELECT COALESCE(MAX(messageId),0) FROM "{OTHER_USERNAME}";'''
                        cur.execute(query)
                        maxId = cur.fetchall()[0][0] + 1

                        # 
                        query = f'''INSERT INTO "{OTHER_USERNAME}"
                                    VALUES('{MY_USERNAME}', '{message}', {maxId});'''
                        cur.execute(query)

                        # 
                        query = f'''UPDATE connections SET readUpto = {maxId} WHERE username = '{OTHER_USERNAME}';'''
                        cur.execute(query)
                        
                        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
                        jsonData = json.dumps({'userMessage': f"{message}", 'sender': f"{MY_USERNAME}",
                                              'receiver': f"{OTHER_USERNAME}", 'isGroup': isGroup, 'isAck': False})
                        client_socket.send(
                            bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))

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
