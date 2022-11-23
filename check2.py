import socket

IP = 'localhost'
PORT = 6000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)
client_socket.send(bytes(f'hello', encoding='utf-8'))
while True:
    message = client_socket.recv(1024)
    if(message):
        break
print("kshdsihds")
print(message.decode('utf-8'))