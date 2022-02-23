import socket  # used to establish network connection
import threading  # used for multithreading

# Connection data
host = '127.0.0.1'
port = 55321

# Start the server
# param1: use an internet socket, param2: use TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()  # listen for incoming connections
print("Server is listening...")

# Listen for Clients and their Nicknames
clients = []
nicknames = []

# Broadcast messages to all clients


def broadcast(message):
    for client in clients:
        client.send(message)

# Handling Messages From Clients


def handle(client):
    while True:
        try:
            # Broadcasting Messages
            msg = message = client.recv(1024)
            if msg.decode('ascii').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = msg.decode('ascii')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send('Command was refused.'.encode('ascii'))
            elif msg.decode('ascii').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned.')
                else:
                    client.send('Command was refused.'.encode('ascii'))
            else:
                broadcast(message)
        except:
            # Removing And Closing Clients
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} left the chat.'.encode('ascii'))
                nicknames.remove(nickname)
                break

# Receiving / Listening Function


def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        # Request And Store Nickname
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')

        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        if nickname+'\n' in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue

        if nickname == 'admin':
            client.send('PASS'.encode('ascii'))
            password = client.recv(1024).decode('ascii')

            if password != 'admin':
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue  # don't break, just skip this loop since we have a sole thread for listening

        nicknames.append(nickname)
        clients.append(client)

        # Print And Broadcast Nickname
        print(f'Nickname is {nickname}')
        broadcast("{} joined!".format(nickname).encode('ascii'))
        client.send('Connected to server!'.encode('ascii'))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


def kick_user(user):
    if user in nicknames:
        name_index = nicknames.index(user)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked by an admin'.encode('ascii'))
        client_to_kick.close()
        nicknames.remove(user)
        broadcast(f'{user} was kicked by an admin'.encode('ascii'))


receive()
