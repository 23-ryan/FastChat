import socket
import select

if __name__ == '__main__':

    IP = 'localhost'
    PORT = 6000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))

    server_socket.listen()

    print(f'Listening for connections on {IP}:{PORT}...')
    while True:
        conn, address = server_socket.accept()
        message = conn.recv(1024)
        print(message.decode('utf-8'))
        print("dshd")
        conn.send(bytes(f'hi', encoding='utf-8'))
        print("dshd")
