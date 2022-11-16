# from colorama import init
from signIn import handleSignIn
from signUp import handleSignUp
from termcolor import colored
from client import addNewDM, getAllUsers, isInConnections
import xmlrpc.client as cl
import sys

IP = sys.argv[1]
PORT = int(sys.argv[2])
proxy = cl.ServerProxy(f"http://{IP}:{PORT}/")

MY_USERNAME = ""

# Chat name
print(colored("        NAWAB CHAT", 'green'))
print("===========================\n")

# options list
print(colored("OPTIONS", 'red'))
print('1.', colored("SIGN IN", 'blue'))
print('2.', colored("SIGN UP", 'blue'))

choice = input("\nType your choice: ")

while True:
    if(choice == '1'):
        MY_USERNAME = handleSignIn(proxy)
        break
    elif(choice == '2'):
        MY_USERNAME = handleSignUp(proxy)
        break
    else:
        continue


while True:
    print(colored("\nUSER OPTIONS", 'red'))
    print("------------")
    print('1.', colored("ADD USER", 'blue'))
    print('2.', colored("CHAT", 'blue'))
    print('3.', colored("CREATE GROUP", 'blue'))
    print('4.', colored("SETTINGS", 'blue'))
    print('5.', colored("EXIT", 'blue'))


    choice = input("\nType your choice: ")

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

            print(colored("\nGROUP", 'red'))
            print("-----")
            for i in group:
                print(colored(i, 'blue'))
                
            chatWithUser = input("Enter name of the user to chat with: ") 

        elif(choose == '2'):
            chatWithUser = input("Enter name of the user to chat with: ")
        
        if(chatWithUser in DM):
            print("----->")
        elif(chatWithUser in group):
            print("----->")
        else:
            print(colored("INVALID USERNAME!",'yellow'))
            continue

    elif(choice == '5'):
        sys.exit()

