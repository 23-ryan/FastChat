import socket
import threading
nickname = input("Choose your nickname: ")

# socket initialization
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 4000))  # connecting client to server


def receive():
    while True:  # making valid connection
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICKNAME':
                client.send(nickname.encode('utf-8'))
            elif message == 'YOU ARE BEING KICKED':
                # we have been kicked
                print("You are no longer a participant in this group")
                client.close()
                break
            else:
                print(message)
        except:  # case on wrong ip/port details
            print("An error occured!")
            client.close()
            break


def write():
    while True:  # message layout
        message = '{}: {}'.format(nickname, input(''))
        client.send(message.encode('utf-8'))


receive_thread = threading.Thread(target=receive)  # receiving multiple messages
receive_thread.start()

write_thread = threading.Thread(target=write)  # sending messages
write_thread.start()



