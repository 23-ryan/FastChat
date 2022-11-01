import os
import socket
import select
import errno
import sys
import json
import base64

HEADER_LENGTH = 10

IP = "192.168.0.106"
PORT = 3000
my_username = input("Username: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((IP, PORT))
client_socket.setblocking(False)
username = my_username
username_header = f"{len(username):<{HEADER_LENGTH}}"
data = {'userHeader':f"{username_header}", 'userMessage':f"{username}"}
jsonData = json.dumps(data)
client_socket.send(bytes(jsonData, encoding='utf-8'))

sockets_list = [sys.stdin, client_socket]

while True:
    try:
        read_sockets, _, error_sockets = select.select(sockets_list,[], sockets_list)
        for sockets in read_sockets:
            # LEAVE GROUP message
            if(client_socket == sockets):
                data = client_socket.recv(4196540)
                data = json.loads(data.decode('utf-8'))
                # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                if not len(data):
                    print('Connection closed by the server')
                    sys.exit()
                
                # print(data)
                username_length = int(data['usernameLen'])
                username = data['userName']

                message_length = int(data['messageLen'])
                message = data['message']

                if message == "SEND IMAGE":
                    ans = input("DO YOU WANT TO RECIEVE AN IMAGE SENT(YES/NO ?):")
                    if(ans.upper() == "YES"):
                        os.system(f'touch image.{data["imageFormat"]}')
                        with open(f'image.{data["imageFormat"]}', 'wb') as f:
                            f.write(base64.b64decode(data["imageData"]))

                print(f'{username} > {message}')

            else:
                message = sys.stdin.readline()[0:-1]
                if message == "LEAVE GROUP":
                    message = message.encode('utf-8')
                    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8') # It is a string with length="HEADER_LENGTH" and with the number "len(message) alligned to its left"
                    client_socket.send(message_header + message)
                    print("You are no longer a participant of this group")
                    sys.exit()

                elif message == "SEND IMAGE":
                    path = input("PATH OF IMAGE: ")
                    img_json = ""
                    if(path != ""):
                        with open(path, 'rb') as f:
                            img_json = {'userHeader':f"{len(message):<{HEADER_LENGTH}}", 'userMessage':f"{message}", 'imageFormat': f"{path.split('.')[-1]}", 'imageData':f"{base64.encodebytes(f.read()).decode('utf-8')}"}
                        
                        jsonData = json.dumps(img_json)
                        client_socket.send(bytes(jsonData, encoding='utf-8'))
        

                elif message:
                    # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
                    message_header = f"{len(message):<{HEADER_LENGTH}}"
                    jsonData = json.dumps({'userHeader':f"{message_header}", 'userMessage':f"{message}"})
                    client_socket.send(bytes(jsonData, encoding='utf-8'))

            
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