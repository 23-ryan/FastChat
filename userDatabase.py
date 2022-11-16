import psycopg2
from datetime import datetime
import os
import sys

conn = psycopg2.connect(database ="postgres", user = "postgres", password = "psql", host = "localhost", port = "5432")
conn.autocommit = True
cur = conn.cursor()
name = input("TYPE USERNAME: ")


cur.execute(f'''DROP DATABASE IF EXISTS {name}''')
cur.execute(f"CREATE DATABASE {name};")
conn = psycopg2.connect(database =f"{name}", user = "postgres", password = "psql", host = "localhost", port = "5432")
conn.autocommit = True
cur = conn.cursor()


connectTo = input('FRIEND: ')
cur.execute(f'''DROP TABLE IF EXISTS {connectTo}''')
cur.execute(f'''CREATE TABLE {connectTo}(
            message TEXT,
            time INT
);''')

cur.execute(f'''INSERT INTO {connectTo} 
                VALUES('YOU ARE MY FRND', 12);''')
conn.commit()

cur.execute(f"SELECT * FROM {connectTo}")
print(cur.fetchall())