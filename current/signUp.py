import rsa
from server import addNewUser
from server import checkUserName
from termcolor import colored

def handleSignUp():
    userName = input("User Name: ")
    if (not checkUserName(userName)):
        password = input("Password: ")

        publickey, privatekey = rsa.newkeys(48)
        addNewUser(userName, password, publickey)
        print(colored('USER SUCCESSFULLY REGISTERED !!', 'yellow'))

        # CREATE CONNECTIONS TABLE
        
        return

    else:
        print("INVALID USERNAME! ")
        handleSignUp()
