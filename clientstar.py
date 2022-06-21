# Importing necessary libraries
import socket  
import threading

from datetime import datetime # Importing datetime to view timestamps

ADDR = ('127.0.0.1', 15662) #IP  and PORT tuple
ENCODING = 'utf-8' # UTF-8 type encoding is followed here


#this function handles the responses sent from the server to the client
def handle_server_instruction(message):
    
    if message == '%USER%':
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

#This function receives the information transmitted from the server and passes to the handle_server_instruction function
def receive():
    
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

# this is the function from where we will write to the server
def write():
    
    while True:
        now = datetime.now()
        time = now.strftime("%H : %M : %S")
        message = f'{input("")}'
        co.send(message.encode(ENCODING))


        #main function which gets called as soon as we initiate the client file
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
