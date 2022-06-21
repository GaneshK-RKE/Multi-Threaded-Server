#importing necessary libraries

import threading
import socket

from datetime import datetime


encoding = 'utf-8' #encoding which we follow here is utf-8
decoding = 'utf-8' # same as encoding
ADDR = ('127.0.0.1', 15662) #address tuple



#initiating a class USER so that we fan use the values of client object (co in this case elsewhere)
class User:
    def __init__(self, username: str, co: socket, admin_only=False):
        self.username = username
        self.co = co
        self.admin_only = admin_only

# A function which will send the message to all the participants in the hosted sserver
def broadcast(message: str, ignore_list=None, admin_only=False):
   
    for user in users:
        if not admin_only :
            user.co.send(message.encode(encoding))
        
                

# A function which sends the messages to the client
def send_to(user: User, message: str):
    return user.co.send(message.encode(encoding))

# A function to receive from the client
def receive_from(user: User, size: int = 1024):
    return user.co.recv(size).decode(decoding)

# Kicking users function
def kick_user(username: str):
    try:
        user_idx = list(map(lambda p: p.username, users)).index(username) # A lambda function is used for convinience
    except ValueError:
        now = datetime.now()
        time = now.strftime("%H : %M : %S")
        print(f'{time} / Could not kick {username} -- user not found')
        return False
    user_to_kick = users[user_idx]
    users.remove(user_to_kick)
    send_to(user_to_kick, '-- You have been kicked by an admin')
    user_to_kick.co.close()
    now = datetime.now()
    time = now.strftime("%H : %M : %S")
    print(f'{time} / {user_to_kick} was kicked by {username}')
    broadcast(f'{time} / {user_to_kick} was kicked by {username}')
    return True

# A function which handles different commands from the client
def handle_command(user, message):
    now = datetime.now()
    time = now.strftime("%H : %M : %S")
    print(f'{time} /Command by {user.username}: "{message}"')
    cmd: str = message.strip()
    cmd_name = cmd.split(' ', 1)[0]
    
    
    if cmd_name == '$admin': # A command to activate admin-only commands
        send_to(user, '%PASS%')
        passww = receive_from(user)
        if passww == '12345': # we have set the password here to 12345
            user.admin_only = True
            now = datetime.now()
            time = now.strftime("%H : %M : %S")
            print(f'{time} /  {user.username} is now an admin')
            send_to(user, '---> Congrats! You are an Avenger now :P')
            broadcast(f'--->>  {user.username} is now an admin', [user], True)
        else:
            send_to(user, '-- Invalid credentials')
    #Non-Admin commands
    elif cmd_name == '$quit' or cmd_name == '$exit':
        send_to(user, '%QUIT%')
        user.co.close()
    elif cmd_name == '$online':
        send_to(user, f'-- Currently online users: {list(map(lambda p: p.username, users))}')
    
    #Admin commands below
    elif not user.admin_only:
        send_to(user, '-- Admin privileges required')
    else:
        if cmd_name == '$kick': # To kick out a user
            username_to_kick = cmd[6:]
            if kick_user(username_to_kick):
                broadcast(f'-->> {username_to_kick} was kicked by {user.username}', None, True)
            else:
                send_to(user, f'-- Could not kick {username_to_kick}')
        elif cmd_name == '$ban': # To ban a user
            username_to_ban = cmd[5:]
            if kick_user(username_to_ban):
                banned_usernames.append(username_to_ban)
                broadcast(f'-- User {username_to_ban} kicked and banned by {user.username}', None, True)
            else:
                send_to(user, f'-- Could not kick {username_to_ban}')
        elif cmd_name == '$unban': # To unban a user
            username_to_unban = cmd[7:]
            try:
                banned_usernames.remove(username_to_unban)
                broadcast(f'-- User {username_to_unban} unbanned by {user.username}', None, True)
            except ValueError:
                send_to(user, f'-- User {username_to_unban} was not in ban list')
        elif cmd_name == '$banned': # shows the current list of banned users
            send_to(user, f'-- Currently banned: {banned_usernames}')
        else:
            send_to(user, '-- Invalid command')

# A function to handle clients
def handle(user: User):
    
    while True:
        try:
            message = receive_from(user)
            if message.startswith('$'):
                handle_command(user, message)
            else:
                broadcast(f'{user.username}: {message}', [user])
        except Exception as e:
            now = datetime.now()
            time = now.strftime("%H : %M : %S")
            print(f'{time} / {e}')
            try:
                users.remove(user)
                user.co.close()
                broadcast(f'-- {user.username} left the chat')
            finally:
                break

# A function to receive from the client
def receive():
    
    while True:
        co, address = server.accept()
        now = datetime.now()
        time = now.strftime("%H : %M : %S")
        print(f'{time} /Connected with {str(address)}')
        
        # These following are sent to the client to invoke several differnt actions
        co.send('%NICK%'.encode(encoding))
        username = co.recv(1024).decode(encoding)
        if username in banned_usernames:
            now = datetime.now()
            time = now.strftime("%H : %M : %S")
            print(f'{time} /Connection attempt with banned username: "{username}"')
            co.send('%BANNED%'.encode(encoding))
        else:
            if username in list(map(lambda p: p.username, users)):
                now = datetime.now()
                time = now.strftime("%H : %M : %S")
                print(f'{time} /Connection attempt with existing username: "{username}"')
                co.send('%DUPLICATE%'.encode(encoding))
            else:
                new_user = User(username, co)
                users.append(new_user)

                now = datetime.now()
                time = now.strftime("%H : %M : %S")

                print(f'{time} /New user: {username}')
                broadcast(f'---->> {username} joined the chat!', [new_user])
                send_to(new_user, '-- Connected to server!')

                thread = threading.Thread(target=handle, args=(new_user,))
                thread.start()

# Main function
if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()

    users = []
    banned_usernames = []

    now = datetime.now()
    time = now.strftime("%H : %M : %S")

    print(f'{time} / The Server Kernel is started and is ready for new connections ')
    receive()
