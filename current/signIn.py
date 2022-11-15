import rsa
from server import addNewUser,isValidPassword, checkUserName
from termcolor import colored
from termcolor import colored

def handleSignIn():
    userName = input("USER NAME: ")
    if(not checkUserName(userName)):
        print(colored("USER DOES NOT EXIST!!", 'yellow'))
    else:
        password = input("PASSWORD: ")
        if(isValidPassword(userName, password)):
            print(colored("LOGIN SUCCESSFUL!!", 'yellow'))
