import psycopg2
from server import IP
serverDbName = "fastchat"


def connectToDb():
    """Connect to the appropriate PostgreSQL account and set autocommit to true.

    :return: cursor to the server database
    :rtype: _Cursor
    """
    conn = psycopg2.connect(database=f"{serverDbName}", user="postgres",
                            password="fastchat", host=IP, port="5432")
    conn.autocommit = True
    cur = conn.cursor()
    return cur
