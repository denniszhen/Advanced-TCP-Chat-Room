import socket
import threading

# Choosing Nickname
nickname = input("Choose your nickname: ")
if nickname == 'admin':
    password = input("Enter admin password:")


# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8080))

# Listening to Server and Sending Nickname


def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':  # Get asked for the nickname
                # Send the nickname to the server
                client.send(nickname.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')
                if next_message == 'PASS':  # If server requests password because your nickname was 'admin'
                    # Send the password to the server
                    client.send(password.encode('ascii'))
                    # If the password was wrong
                    if client.recv(1024).decode('ascii') == 'REFUSE':
                        print("Connection refused. Wrong password.")
                        stop_thread = True  # Stop the thread
                elif next_message == 'BAN':
                    print("Connection refused because of ban")
                    client.close()
                    stop_thread = True
            else:
                print(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            client.close()
            break

# Sending Messages To Server


def write():
    while True:
        if stop_thread:  # Break the write loop if the global stop_thread variable is true
            break
        message = '{}: {}'.format(nickname, input(''))
        # Escape the username, colon, and space to see if a command is being executed
        if message[len(nickname)+2].startswith('/'):
            if nickname == 'admin':  # if admin user
                if message[len(nickname)+2].startswith('/kick'):  # if kick command is entered
                    # send kick command to the server
                    client.send(
                        'KICK {message[len(nickname)+2+6]}'.encode('ascii'))
                # if ban command is entered
                elif message[len(nickname)+2].startswith('/ban'):
                    # send ban command to the server
                    client.send(
                        'BAN {message[len(nickname)+2+5]}'.encode('ascii'))
            else:
                # if command was entered by non-admin user
                print("Commands can only be executed by admins")
        else:
            # if the message wasn't a command to begin with, send it normally
            client.send(message.encode('ascii'))


# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
