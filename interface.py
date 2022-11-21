# from colorama import init
from signIn import handleSignIn
from signUp import handleSignUp
from termcolor import colored
from client import checkSocketReady
from client import addNewDM, getAllUsers, isInConnections
from DM import handleDM
from handleGroup import handleGroup
from client import receive_message, unpack_message, createGroup, isAdminOfGroup, getPrivateKey
import xmlrpc.client as cl
import select
import sys
import json
import socket

RPC_PORT = 4000
IP = sys.argv[1]
PORT = int(sys.argv[2])
proxy = cl.ServerProxy(f"http://{IP}:{RPC_PORT}/", allow_none=True)

MY_USERNAME = ""

# Initializing the client socket
HEADER_LENGTH = 10

IP = sys.argv[1]
PORT = int(sys.argv[2])
# my_username = input("Username: ")


# Chat name
print(colored("        NAWAB CHAT", 'green'))
print("===========================\n")

# options list
print(colored("OPTIONS", 'red'))
print('1.', colored("SIGN IN", 'blue'))
print('2.', colored("SIGN UP", 'blue'))
print('3.', colored("EXIT", 'blue'))

choice = input("\nType your choice: ")


#############
# IF USER MISTYPE HIS NAME THEN ON RETRYING THE SYSTEM EXITS ?? ---> ERROR
#############
while True:
    if(choice == '1'):
        MY_USERNAME, client_socket = handleSignIn(proxy, IP, PORT)
        print(client_socket)
        break
    elif(choice == '2'):
        MY_USERNAME, client_socket = handleSignUp(proxy, IP, PORT)
        print(client_socket)
        break
    elif(choice == '3'):
        sys.exit()
    else:
        continue

socket_list = [sys.stdin, client_socket]

while True:
    print(colored("\nUSER OPTIONS", 'red'))
    print("------------")
    print('1.', colored("ADD USER", 'blue'))
    print('2.', colored("ADD USER TO A GROUP", 'blue'))
    print('3.', colored("CHAT", 'blue'))
    print('4.', colored("CREATE GROUP", 'blue'))
    print('5.', colored("SETTINGS", 'blue'))
    print('6.', colored("EXIT", 'blue'))


    print("\nType your choice: ")
    read_sockets, _, error_sockets = select.select(socket_list,[], socket_list)
    for socket in read_sockets:
        if(socket == client_socket):
            print("IN")
            # if(checkSocketReady(client_socket)):
            data = unpack_message(client_socket)
            receive_message(data, proxy)
            print("OUT")
    
        else:
            choice = sys.stdin.readline()[0:-1]
            # print(choice)
            if(choice == '1'):
                username = input("Enter username to be added: ")
                if(not isInConnections(MY_USERNAME, username)):
                    if(not addNewDM(MY_USERNAME, username, proxy)):
                        print(colored("INVALID USERNAME!!\n",'yellow'))
                        continue
                    print(colored("SUCCESSFULLY ADDED!!", 'yellow'))
                    continue

                print(colored("USER ALREADY CONNECTED!!", 'yellow'))
                continue

            elif(choice == '2'):
                grpName = input("ENTER GROUP NAME: ")
                if(not proxy.checkUserName(grpName)):
                    print(colored("INVALID GROUP NAME!!", 'yellow'))
                else:
                    if(isAdminOfGroup(grpName,MY_USERNAME)):
                        newuser = input("NEW PARTICIPANT: ")
                        if(proxy.checkUserName(newuser)):
                            proxy.addUserToGroup(grpName, newuser)

                            # SENDING KEYWORD TO ADD THE GROUP TO THE NEW USER SIDE
                            message = "ADD_PARTICIPANT"
                            jsonData = json.dumps({'userMessage':f"{message}",'sender':f"{MY_USERNAME}", 'receiver':f"{newuser}", 'grpName':f"{grpName}", 'privateKey':getPrivateKey(grpName, MY_USERNAME), 'isGroup':False})
                            client_socket.send(bytes(f'{len(jsonData):<10}{jsonData}', encoding='utf-8'))
                        else:
                            print(colored("USER DOESN'T EXIST!!", 'yellow'))
                    else:
                        print(colored(f"ADMIN PRIVILEGES NOT AVAILABLE FOR GROUP:{grpName}", 'yellow'))
                ## QUERY ABOUT THE ADMIN USER ##


            elif(choice == '3'):
                print('1.', colored("LIST CONNECTIONS", 'green'))
                print('2.', colored("SEARCH", 'green'))
                print('3.', colored("BACK", 'green'))
                

                DM, group = getAllUsers(MY_USERNAME)
                
                chatWith = ""
                choose = input("Choice: ")
                if(choose == '3'):
                    break
                if(choose == '1'):
                    print(colored("USERS", 'red'))
                    print("-----")
                    for i in DM:
                        print(colored(i, 'blue'))

                    print(colored("\nGROUP", 'red'))
                    print("-----")
                    for i in group:
                        print(colored(i, 'blue'))
                        
                    chatWith = input("Enter name of the user to chat with: ")

                elif(choose == '2'):
                    chatWith = input("Enter name of the user to chat with: ")
                
                if(chatWith in DM):
                    print("----->")
                    handleDM(MY_USERNAME, chatWith, client_socket, proxy, False)
                elif(chatWith in group):
                    print("----->")
                    handleDM(MY_USERNAME, chatWith, client_socket, proxy, True)
                    # handleGroup(MY_USERNAME, chatWith, client_socket, proxy)
                else:
                    print(colored("INVALID USERNAME!",'yellow'))
                    continue

            elif(choice == '4'):
                grpName = input("ENTER GROUP NAME: ")
                createGroup(grpName, MY_USERNAME, proxy)
                print(colored('GROUP SUCCESSFULLY CREATED!!', 'yellow'))
                
            elif(choice == '6'):
                sys.exit()
            else:
                print(colored("INVALID OPTION!!", 'yellow'))
                continue

