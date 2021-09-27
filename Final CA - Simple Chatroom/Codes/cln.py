import socket
import select
import pickle
import errno

HEADER_LENGTH = 1024

IP = "127.0.0.1"
PORT = 1234
my_username = input("Username: ")

# Creating a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connecting to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call wont block them: 
client_socket.setblocking(False)

# Creating a Username and header
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

while True:

    # Receive the clients list regardless of the user choosing list cause we need to know if there is a client to send a message to or not:
    
    clients = pickle.loads(clients)
    users = clients[client_socket]['data'].decode('utf-8')

    # Wait for user to choose an option
    choice = int(input('Welcome to the Chatroom. Enter the corresponding number for each order. (1:LIST/2:SEND/3:RECIEVE/4:EXIT)'))



    # Dividing the scenarios:
    # LIST:
    if (choice == 1):

        print("Printing existing users in the chatroom:\n") 
        print(*users, sep = "\n")


    # SEND:
    elif (choice==2):

        rcv_name = str(input('Please Enter recievers username:'))
        if rcv_name in users:
             message = input(f'{my_username} > ')

          # For a non-empty message:
             if message:
        
         # Sending encoded message with its recievers name:
               message = message.encode('utf-8')
               message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
               client_socket.send(message_header + message + ' '+ rcv_name)

        else:
             print("Reciever not found in the chatroom right now!, Please try later...")


    # RECEIVE:
    elif (choice==3):
    
        try:
            # Loop over all received message to see whether a message is intended for us or not:
            while True:

                username_header = client_socket.recv(HEADER_LENGTH)

                # If no message is received the header length will be 0:
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()

                # Convert header to int value:
                username_length = int(username_header.decode('utf-8').strip())

                # Receive and Decode the username:
                username = client_socket.recv(username_length).decode('utf-8')

                # Repeat the receiving and decoding steps for the message part:

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())

                message = client_socket.recv(message_length).decode('utf-8')



                # The message sent by another client consists the reciever name at the end, we should spit it to investigate whether its for us or not:
                splitted =  message.split()
                pure_message = splitted[0]
                receiver = splitted[1]

                # Print the message if its intended for you
                if (reciever == my_username):
                    print(pickle(loads(f'{username} > {pure_message}')))

               

        except IOError as e:
            # In case of an Input-Output error: 

            if (e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK):
               print('Reading error: {}'.format(str(e)))
               sys.exit()

        # If We didn't receive anything:
        
        

        except Exception as e:
               # In case of any other exception:
                print('Reading error: '.format(str(e)))
                sys.exit()
        continue

    # EXIT:
    elif (choice==4):

        # Client exits the cahtroom
        sys.exit() 

    else:
        print("\nInvalid order! Please try again!")
 