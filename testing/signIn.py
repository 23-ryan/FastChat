import rsa
# from server import addNewUser,isValidPassword, checkUserName
from termcolor import colored
from client import goOnline
# from interface import IP, PORT

def handleSignIn(proxy, IP, PORT):
    userName = input("USER NAME: ")
    if(not proxy.checkUserName(userName)):
        print(colored("USER DOES NOT EXIST!!", 'yellow'))
        handleSignIn(proxy, IP, PORT)
    else:
        password = input("PASSWORD: ")
        if(proxy.isValidPassword(userName, password)):
            print(colored("LOGIN SUCCESSFUL!!", 'yellow'))
            client_socket = goOnline(userName, IP, PORT)
        return userName, client_socket
