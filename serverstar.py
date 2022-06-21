

# Importing necessary libraries
import threading
import socket

from datetime import datetime


encoding = 'utf-8'# utf encoding
decoding = 'utf-8'# utf decoding
ADDR = ('127.0.0.1', 15662)# address tuple



# a user class is initiated so that we can use these usernames and the socket object at other places as well
class User:
    def __init__(self, username: str, co: socket, is_admin=False):
        self.username = username
        self.co = co
        self.is_admin = is_admin

# a function which sends the messages to all the current participants in the server
def broadcast(message: str, ignore_list=None, admin_only=False):
    if ignore_list is None:
        ignore_list = []
    for user in users:
        if user not in ignore_list:
            if not admin_only or user.is_admin:
                user.co.send(message.encode(encoding))

# a function to send the commands to the clients
def send_to(user: User, message: str):
    return user.co.send(message.encode(encoding))

# a function to receive from the clients
def receive_from(user: User, size: int = 1024):
    return user.co.recv(size).decode(decoding)

#a function to kick user ( requires admin prvilidges)
def kick_user(username: str):
    try:
        user_idx = list(map(lambda p: p.username, users)).index(username)
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
    print(f'{time} /Kicked {username}')
    broadcast(f'-- {username} has been kicked')
    return True

#a function to handle differnt commands rev=ceived from the clients
def handle_command(user, message):
    now = datetime.now()
    time = now.strftime("%H : %M : %S")
    print(f'{time} /Command by {user.username}: "{message}"')
    cmd: str = message.strip()
    cmd_name = cmd.split(' ', 1)[0]
    # non-admin commands
    if cmd_name == '$admin':
        send_to(user, '%PASS%')
        passww = receive_from(user)
        if passww == '12345':
            user.is_admin = True
            now = datetime.now()
            time = now.strftime("%H : %M : %S")
            print(f'{time} /  {user.username} is now an admin')
            send_to(user, '---> Congrats! You are and Avenger now ')
            #broadcast(f'-- User {user.username} is now an admin', True)
        else:
            send_to(user, '-- Invalid credentials')
    elif cmd_name == '$quit' or cmd_name == '$exit':
        send_to(user, '%QUIT%')
        user.co.close()
    elif cmd_name == '$online':
        send_to(user, f'-- Currently online users: {list(map(lambda p: p.username, users))}')
    # admin commands
    elif not user.is_admin:
        send_to(user, '-- Admin privileges required')
    else:
        if cmd_name == '$kick':
            username_to_kick = cmd[6:]
            if kick_user(username_to_kick):
                broadcast(f'-->> {username_to_kick} was kicked by {user.username}', None, True)
            else:
                send_to(user, f'-- Could not kick {username_to_kick}')
        elif cmd_name == '$ban':
            username_to_ban = cmd[5:]
            if kick_user(username_to_ban):
                banned_usernames.append(username_to_ban)
                broadcast(f'-- User {username_to_ban} kicked and banned by {user.username}', None, True)
            else:
                send_to(user, f'-- Could not kick {username_to_ban}')
        elif cmd_name == '$unban':
            username_to_unban = cmd[7:]
            try:
                banned_usernames.remove(username_to_unban)
                broadcast(f'-- User {username_to_unban} unbanned by {user.username}', None, True)
            except ValueError:
                send_to(user, f'-- User {username_to_unban} was not in ban list')
        elif cmd_name == '$banned':
            send_to(user, f'-- Currently banned: {banned_usernames}')
        else:
            send_to(user, '-- Invalid command')

#A function to handle the clients 
def handle(user: User):
    """
    Handle each new input from user;
    this method runs in a separate thread for each user
    """
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

# function to receive from  the client
def receive():
    """
    Main loop, add new clients to the chat room
    """
    while True:
        co, address = server.accept()
        now = datetime.now()
        time = now.strftime("%H : %M : %S")
        print(f'{time} /Connected with {str(address)}')

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
                broadcast(f'-- User {username} joined!', [new_user])
                send_to(new_user, '-- Connected to server!')

                thread = threading.Thread(target=handle, args=(new_user,))
                thread.start()

# main function
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
