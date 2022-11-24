import psycopg2
from datetime import datetime
import os
import sys

serverDbName = "fastchat"


def connectToDb():
    """Connect to the appropriate PostgreSQL account and set autocommit to true.

    :return: cursor to the server database
    :rtype: _Cursor
    """
    conn = psycopg2.connect(database=f"{serverDbName}", user="postgres",
                            password="fastchat", host="localhost", port="5432")
    conn.autocommit = True
    cur = conn.cursor()
    return cur
