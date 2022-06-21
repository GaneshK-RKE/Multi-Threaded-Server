import threading
import socket

from datetime import datetime


encoding = 'utf-8'
decoding = 'utf-8'
ADDR = ('127.0.0.1', 15662)
#AUTHORIZED_ADMIN_CREDENTIALS = ['admin:adminpassww', 'joe:secure']



class User:
    def __init__(self, username: str, co: socket, admin_only=False):
        self.username = username
        self.co = co
        self.admin_only = admin_only


def broadcast(message: str, ignore_list=None, admin_only=False):
    if ignore_list is None:
        ignore_list = []
    for user in users:
        if user not in ignore_list:
            if not admin_only or user.admin_only:
                user.co.send(message.encode(encoding))


def send_to(user: User, message: str):
    return user.co.send(message.encode(encoding))


def receive_from(user: User, size: int = 1024):
    return user.co.recv(size).decode(decoding)


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
    print(f'{time} / {user_to_kick} was kicked by {username}')
    broadcast(f'{time} / {user_to_kick} was kicked by {username}')
    return True


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
            user.admin_only = True
            now = datetime.now()
            time = now.strftime("%H : %M : %S")
            print(f'{time} /  {user.username} is now an admin')
            send_to(user, '---> Congrats! You are an Avenger now :P')
            broadcast(f'--->>  {user.username} is now an admin', [user], True)
        else:
            send_to(user, '-- Invalid credentials')
    elif cmd_name == '$quit' or cmd_name == '$exit':
        send_to(user, '%QUIT%')
        user.co.close()
    elif cmd_name == '$online':
        send_to(user, f'-- Currently online users: {list(map(lambda p: p.username, users))}')
    # admin commands
    elif not user.admin_only:
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
                broadcast(f'---->> {username} joined the chat!', [new_user])
                send_to(new_user, '-- Connected to server!')

                thread = threading.Thread(target=handle, args=(new_user,))
                thread.start()


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