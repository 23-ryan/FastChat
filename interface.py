# from colorama import init
from signIn import handleSignIn
from signUp import handleSignUp
from termcolor import colored
from client import checkSocketReady
from client import addNewDM, getAllUsers, isInConnections
from DM import handleDM
from client import receive_message, unpack_message
import xmlrpc.client as cl
import select
import sys
import json
import socket

RPC_PORT = 3000
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
    else:
        continue

socket_list = [sys.stdin, client_socket]

while True:
    print(colored("\nUSER OPTIONS", 'red'))
    print("------------")
    print('1.', colored("ADD USER", 'blue'))
    print('2.', colored("CHAT", 'blue'))
    print('3.', colored("CREATE GROUP", 'blue'))
    print('4.', colored("SETTINGS", 'blue'))
    print('5.', colored("EXIT", 'blue'))


    read_sockets, _, error_sockets = select.select(socket_list,[], socket_list)
    for socket in read_sockets:
        if(socket == client_socket):
            print("IN")
            # if(checkSocketReady(client_socket)):
            data = unpack_message(client_socket)
            receive_message(data, proxy)
            print("OUT")
    
        else:
            print("\nType your choice: ")
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
                print('1.', colored("LIST CONNECTIONS", 'green'))
                print('2.', colored("SEARCH", 'green'))
                
                DM, group = getAllUsers(MY_USERNAME)
                
                chatWithUser = ""
                choose = input("Choice: ")
                if(choose == '1'):
                    print(colored("USERS", 'red'))
                    print("-----")
                    for i in DM:
                        print(colored(i, 'blue'))

                    print(colored("\nGROUP", 'red'      ))
                    print("-----")
                    for i in group:
                        print(colored(i, 'blue'))
                        
                    chatWithUser = input("Enter name of the user to chat with: ")

                elif(choose == '2'):
                    chatWithUser = input("Enter name of the user to chat with: ")
                
                if(chatWithUser in DM):
                    print("----->")
                    handleDM(MY_USERNAME, chatWithUser, client_socket, proxy)
                elif(chatWithUser in group):
                    print("----->")
                else:
                    print(colored("INVALID USERNAME!",'yellow'))
                    continue

            elif(choice == '5'):
                sys.exit()

