import psycopg2
from datetime import datetime
import os
import sys

serverDbName = "fastchat"

def connectToDb():
    conn = psycopg2.connect(database =f"{serverDbName}", user = "postgres", password = "fastChat", host = "192.168.191.89", port = "5432")
    conn.autocommit = True
    cur = conn.cursor()
    return cur

