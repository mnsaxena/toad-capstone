import socket
import time
import select

#socket config
s = socket.socket() 
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setblocking(0) #set to be nonblocking

connectedclients = 0
poss_readable = [s] #keep track the open sockets 's' being the server itself

HOST = '192.168.1.5' #could be blank, idk really
PORT = 2022 #reserve a port

print("binding port")
s.bind ((HOST, PORT))
s.listen(1) # number of waiting connetions in the buffer
print("Success, starting")

stop_server = 0

'''
connected = False

while connected == False:
    if s:
        conn, addr = s.accept()
        connected = True
        print("connected")

while True:
    data = conn.recv(2000)
    decoded = data.decode('UTF-8')
    print(decoded)
'''

while stop_server == 0:
    try:
        for i in poss_readable:
            if i.fileno() == -1:
                connectedclients -= 1
                poss_readable.remove(i)
                i.close()
        #check the socket for new connections or messages
        (readable, writeable, in_error) = select.select(poss_readable, [], poss_readable, 60)
            

        for i in readable:
            if i is s:
                (clientsocket, addr) = s.accept() #establish connection with a new client
                clientsocket.setblocking(0) 
                poss_readable.append(clientsocket) #add to list of open sockets
                print('Established Connection from ', addr)
                connectedclients += 1
            else:
                message = i.recv(1024) # Get message from the client

                if message:
                    # decode the bytes to string and process
                    decoded = message.decode('UTF-8')
                    print(decoded)
                else:
                    #close the socket to allow reconnection
                    connectedclients -= 1
                    poss_readable.remove(i)
                    i.close() 

                    if connectedclients == 0:
                        stop_server = 1
            
        for i in in_error:
            #close the socket to release resources for a reconnect
            connectedclients -= 1
            poss_readable.remove(i)
            i.close()

            if connectedclients == 0:
                stop_server = 1

        time.sleep(1)

    finally:
        s.close()
