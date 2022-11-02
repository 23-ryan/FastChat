import sqlite3
import os
import sys
import rsa

KEY_LENGTH = 128

connection = sqlite3.connect('fastChat.db')

connection.execute("DROP TABLE IF EXISTS USER_LOGIN_INFO;")
connection.execute('''CREATE TABLE USER_LOGIN_INFO
         (userName TEXT PRIMARY KEY,
         nickName TEXT,
         publicKey INT,
         password TEXT,
         state INT DEFAULT 1);''')

connection.execute("DROP TABLE IF EXISTS GROUPS;")
connection.execute('''CREATE TABLE USER_LOGIN_INFO
         (userName TEXT PRIMARY KEY,
         nickName TEXT,
         publicKey INT,
         password TEXT);''')