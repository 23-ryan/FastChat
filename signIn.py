import rsa
# from server import addNewUser,isValidPassword, checkUserName
from termcolor import colored

def handleSignIn(proxy):
    userName = input("USER NAME: ")
    if(not proxy.checkUserName(userName)):
        print(colored("USER DOES NOT EXIST!!", 'yellow'))
        handleSignIn(proxy)
    else:
        password = input("PASSWORD: ")
        if(proxy.isValidPassword(userName, password)):
            print(colored("LOGIN SUCCESSFUL!!", 'yellow'))
        return userName
