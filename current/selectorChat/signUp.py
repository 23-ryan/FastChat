import rsa
from termcolor import colored

def handleSignUp(proxy):
    userName = input("User Name: ")
    if (not proxy.checkUserName(userName)):
        password = input("Password: ")

        publickey, privatekey = rsa.newkeys(48)
        proxy.addNewUser(userName, password, publickey)
        print(colored('USER SUCCESSFULLY REGISTERED !!', 'yellow'))

        # CREATE CONNECTIONS TABLE
        query = f'''CREATE DATABASE '''
        return

    else:
        print("INVALID USERNAME! ")
        handleSignUp(proxy)
