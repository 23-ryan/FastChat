import sys
import socket
import select
import random
# from itertools import cycle
import threading
from server import *
import time
import os
# dumb netcat server, short tcp connection
# $ ~  while true ; do nc -l 8888 < server1.html; done
# $ ~  while true ; do nc -l 9999 < server2.html; done

# dumb python socket echo server, long tcp connection
# $ ~  while  python server.py
# SERVER_POOL = [('localhost', 6666)]

# ITER = cycle(SERVER_POOL)
# def round_robin(iter):
    # round_robin([A, B, C, D]) --> A B C D A B C D A B C D ...
    # return next(iter)

# class Server(object):
#     def __init__(self, IP, PORT):
#         self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         self.server_socket.bind((IP, PORT))

#         self.sockets_list = [self.server_socket]


#     def addClient(self, client_socket):
#         self.client_sockets_list.append(client_socket)

def getFreeServerId():
    return 0, 5100

def runServer(IP, PORT):
    os.system(f'python3 server.py {IP} {PORT}')

class LoadBalancer(object):
    """ Socket implementation of a load balancer.

    Flow Diagram:
    +---------------+      +-----------------------------------------+      +---------------+
    | client socket | <==> | client-side socket | server-side socket | <==> | server socket |
    |   <client>    |      |          < load balancer >              |      |    <server>   |
    +---------------+      +-----------------------------------------+      +---------------+

    Attributes:
        ip (str): virtual server's ip; client-side socket's ip
        port (int): virtual server's port; client-side socket's port
        algorithm (str): algorithm used to select a server
        flow_table (dict): mapping of client socket obj <==> server-side socket obj
        sockets (list): current connected and open socket obj
    """

    def __init__(self, ip, PORT, algorithm='random'):
        self.ip = ip
        self.port = PORT
        self.algorithm = algorithm
        self.numservers = 3
        

    def startServers(self):
        for i in range(1, self.numservers + 1):
            serverTh = threading.Thread(target=runServer, args=(self.ip, (self.port + 10*i)))
            serverTh.start()
            print("STARTED...")
        
class ServerThread(threading.Thread):
        def __init__(self, IP):
            threading.Thread.__init__(self)
            self.server = SimpleThreadedXMLRPCServer.SimpleXMLRPCServer(
                (IP, 4000), logRequests=False, allow_none=True)
            self.server.register_function(
                isValidPassword)  # just return a string
            self.server.register_function(addNewUser)
            self.server.register_function(checkUserName)
            self.server.register_function(getPublicKey)
            self.server.register_function(createGroupAtServer)
            self.server.register_function(addUserToGroup)
            self.server.register_function(removeUserFromGroup)
            self.server.register_function(getFreeServerId)

        def run(self):
            self.server.serve_forever()


IP = sys.argv[1]
PORT = int(sys.argv[2])

if __name__ == '__main__':
    try:
        # NEW XMLRPC SERVER
        server = ServerThread(IP)
        server.start()
        initialize()

        loadBal = LoadBalancer(f'{IP}', PORT, 'random')
        print(colored("Starting Load Balancer....", 'yellow'))
        # loadBal.startServers()
        time.sleep(1)
    except KeyboardInterrupt:
        print ("Ctrl C - Stopping load_balancer")
        sys.exit(1)