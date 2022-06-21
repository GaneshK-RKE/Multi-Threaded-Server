import socket
import threading

from datetime import datetime

ADDR = ('127.0.0.1', 15662)
ENCODING = 'utf-8'

now = datetime.now()
time = now.strftime("%H : %M : %S")


def handle_server_instruction(message):
    # expected interaction
    if message == '%NICK%':
        co.send(username.encode(ENCODING))
    elif message == '%PASS%':
        passw = input('passw required: ')
        co.send(passw.encode(ENCODING))
    # expected termination
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
        co.close()
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


def receive():
    """Pool messages from server (runs in separate thread)"""
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


def write():
    """Hold open input for sending messages (runs in separate thread)"""
    while True:
        #now = datetime.now()
        #time = now.strftime("%H : %M : %S")
        message = f'{input("")}'
        co.send(message.encode(ENCODING))


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

    receive_threat = threading.Thread(target=receive)
    receive_threat.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()