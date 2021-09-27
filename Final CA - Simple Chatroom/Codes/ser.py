
import socket
import select
import pickle

HEADER_LENGTH = 1024

IP = "127.0.0.1"
PORT = 9000

# Creating a socket:
# socket.AF_INET indicates address family, IPv4
# socket.SOCK_STREAM - TCP, conection-based
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Binding the server:
server_socket.bind((IP, PORT))

# Server should listen to new connections:
server_socket.listen()
sockets_list = [server_socket]

# List of connected clients - socket as a key, User header and name as data
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

# Defining a function for receiving messages:
def receive_message(client_socket):

    try:

        # Receiving header by recieving the stream fo HEADER_LENGTH amount:
        message_header = client_socket.recv(HEADER_LENGTH)

        # Exit the function with False value if there's no message to be recieved
        if not len(message_header):
            return False

        # Converting header to int value to obtain message length
        message_length = int(message_header.decode('utf-8').strip())

        # Returning message header and message data as an object
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # Client has lcoseed or lost its connection
        return False

# The procedure starts here!
while True:

    received_sockets = select.select(sockets_list)


    # Iterating over new sockets connected to the server:
    for new_socket in received_sockets:

        # If new socket is a server socket - new connection, accept it
        if new_socket == server_socket:

            # Accepting the new connection
            client_socket, client_address = server_socket.accept()

            # Client should send his name at the first place so by calling our receive function we recieve its name
            user = receive_message(client_socket)

            # If nothing is recieved - client disconnected before sending his name
            if user is False:
                continue

            # Adding accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save username and username header in our clients list:
            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        #  if there is not a new connection check if existing socket is sending a message:
        else:

            # Receiving message
            message = receive_message(new_socket)

            # If nothing is recieved , client disconnected, cleanup
            if message is False:
                print('Connection closed from: {}'.format(clients[new_socket]['data'].decode('utf-8')))

                # Remove the clients socket from socket list
                sockets_list.remove(new_socket)

                # Remove the client from our list of users
                del clients[new_socket]

                continue

            # Otherwise if there is a message to be sent, first get its senders username:

            user = clients[new_socket]

            print(f'A message is received from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # Iterate over connected clients and broadcast message to all clients, the clients will only print the message for their users if the sender client has intended them as a reciever client (Kinda unicast but still broadcast procedure)
            for client_socket in clients:

                # The only user which shouldnt get the new message is the sender itslef! so:
                if client_socket != new_socket:

                    # Sending user and its message (with their headers)

                    client_socket.sendall(pickle.dumps(user['header'] + user['data'] + message['header'] + message['data']+ "\n"))


