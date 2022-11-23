import sqlite3
import psycopg2
import os
import sys
import rsa

KEY_LENGTH = 128

if __name__ == '__main__':

    conn = psycopg2.connect(database="fastchat", user="postgres",
                            password="fastChat", host="192.168.0.106", port="5432")
    cur = conn.cursor()

    query = '''CREATE TABLE hello(
                userName TEXT PRIMARY KEY,
                id INT,
                password TEXT);'''

    cur.execute(query)
    conn.commit()

    query = '''INSERT INTO hello 
                VALUES ('Yash', 0, 'hail');'''

    cur.execute(query)
    conn.commit()

    query = '''SELECT * FROM hello;'''
    cur.execute(query)
    print(cur.fetchall())
    # connection.execute("DROP TABLE IF EXISTS USER_LOGIN_INFO;")
    # connection.execute('''CREATE TABLE USER_LOGIN_INFO
    #  (userName TEXT PRIMARY KEY,
    #  nickName TEXT,
    #  publicKey INT,
    #  password TEXT,
    #  state INT DEFAULT 1);''')

    # connection.execute("DROP TABLE IF EXISTS GROUPS;")
    # connection.execute('''CREATE TABLE USER_LOGIN_INFO
    #          (userName TEXT PRIMARY KEY,
    #          nickName TEXT,
    #          publicKey INT,
    #          password TEXT);''')
