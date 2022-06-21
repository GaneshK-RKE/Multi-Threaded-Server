#importing necessary libraries
import socket
import threading

from datetime import datetime # this library provides us to have timestamps at our server

ADDR = ('127.0.0.1', 15662) # address tuple consisting of IPV4 and port
ENCODING = 'utf-8' # we are using utf-8 encoding here

now = datetime.now()
time = now.strftime("%H : %M : %S")

# this function handles the information which is recevived from the server
def handle_server_instruction(message):
    # expected interaction
    if message == '%USER%':
        co.send(username.encode(ENCODING))
    elif message == '%PASS%':
        passw = input('passw required: ')
        co.send(passw.encode(ENCODING))
    elif message == '%BANNED%':
        now = datetime.now()
        time = now.strftime("%H : %M : %S")
        print(f'{time} /You are currently banned')
        co.close()
        exit(1)
    elif message == '%DUPLICATE%':
        now = datetime.now()
        time = now.strftime("%H : %M : %S")
        print(f'{time} /This username is already taken, please reconnect with another one')
        co.close() # this command terminates the connection and closes the socket
        exit(1)
    elif message == '%QUIT%':
        now = datetime.now()
        time = now.strftime("%H : %M : %S")
        print(f'{time} /Exiting...')
        co.close()
        exit(0)
    else:
        now = datetime.now()
        time = now.strftime("%H : %M : %S")
        print(f'{time} /Received unknown instruction "{message}" from server')

# A function which helps us receive information from the server
def receive():
    # a while loop is initiated here to terminate for any errors
    while True:
        now = datetime.now()
        time = now.strftime("%H : %M : %S")

        try:
            message = co.recv(1024).decode(ENCODING)
            if message.startswith('%'):
                handle_server_instruction(message)
            else:
                now = datetime.now()
                time = now.strftime("%H : %M : %S")
                print(f'{time} / {message}')
        except OSError:
            now = datetime.now()
            time = now.strftime("%H : %M : %S")
            print(f'{time} /An error occurred!')
            co.close()
            break

# A functio0n to write to the server
def write():
    while True:
        message = f'{input("")}'
        co.send(message.encode(ENCODING))

# Main function which gets initiated when we open this client file
if __name__ == '__main__':
    try:
        username = input("Enter your username: ")

        co = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        co.connect(ADDR)
    except ConnectionRefusedError:
        now = datetime.now()
        time = now.strftime("%H : %M : %S")
        print(f'{time} /Could not connect to the server. Exiting...')
        exit(1)

    receive_threat = threading.Thread(target=receive) # initiating the receive thread
    receive_threat.start()

    write_thread = threading.Thread(target=write) # initiating the write thread
    write_thread.start()
