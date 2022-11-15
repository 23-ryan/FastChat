# from colorama import init
from signIn import handleSignIn
from signUp import handleSignUp
from termcolor import colored


# Chat name
print(colored("        NAWAB CHAT", 'green'))
print("===========================\n")

# options list
print(colored("OPTIONS", 'red'))
print('1.', colored("SIGN IN", 'blue'))
print('2.', colored("SIGN UP", 'blue'))

choice = input("\nType your choice: ")

if(choice == '1'):
    handleSignIn()
elif(choice == '2'):
    handleSignUp()


print(colored("USER OPTIONS", 'orange'))
print("----------------------")
print('1.', colored("ADD USER", 'blue'))
print('2.', colored("CHAT", 'blue'))
print('3.', colored("CREATE GROUP", 'blue'))
print('4.', colored("SETTINGS", 'blue'))

choice = input("\nType your choice: ")

# if(choice == '1'):

