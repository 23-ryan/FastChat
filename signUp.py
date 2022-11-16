import rsa
import psycopg2
from termcolor import colored
from client import connectMydb

# privatekey has 5 components - n,e,d,p,q (inorder) , n,e are in public key too
# so use them wherever needed , only d,p,q corresponding to private key are being stored
# private in connections is for the group case so -1 in case of users and handle seperately 
# for groups

def handleSignUp(proxy):
    userName = input("User Name: ")
    if (not proxy.checkUserName(userName)):
        password = input("Password: ")

        publickey, privatekey = rsa.newkeys(28)
        print(privatekey)
        print(privatekey['d'], privatekey['p'], privatekey['q'])
        proxy.addNewUser(userName, password, publickey['n'], publickey['e'])
        print(colored('USER SUCCESSFULLY REGISTERED !!', 'yellow'))

        # CREATE CONNECTIONS TABLE
        
        cur = connectMydb("postgres")
        query = f'''CREATE DATABASE "{userName}";'''
        cur.execute(query)
        cur = connectMydb(userName)

        query = f'''CREATE TABLE userinfo(
                    username TEXT,
                    password TEXT,
                    publicn BIGINT,
                    publice BIGINT,
                    privated BIGINT,
                    privatep BIGINT,
                    privateq BIGINT);'''
        cur.execute(query)

        query = f'''INSERT INTO userinfo
                    VALUES ('{userName}', '{password}', {publickey['n']}, {publickey['e']}, {privatekey['d']}, {privatekey['p']}, {privatekey['q']});'''
        cur.execute(query)

        query = f'''CREATE TABLE connections(
                    username TEXT,
                    publicn BIGINT,
                    publice BIGINT,
                    privated BIGINT,
                    privatep BIGINT,
                    privateq BIGINT);'''
        cur.execute(query)
        
        return userName

    else:
        print("INVALID USERNAME! ")
        handleSignUp(proxy)
