import xmlrpc.server as Server

port = 8080
class MyServer(Server.SimpleXMLRPCServer):

    def serve_forever(self):
        self.quit = 0
        while not self.quit:
            self.handle_request()

def kill():
    server.quit = 1
    return 1

server = MyServer(('192.168.0.106', port), logRequests=False)
server.register_function()
server.register_function(kill)
server.serve_forever()