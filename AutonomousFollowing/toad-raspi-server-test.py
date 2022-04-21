#libraries for communication
import socket
import sys
import time
import select
#libraries for controlling TOAD
from servoMotor import servo
from rearMotors import motors

# constants
# frame size (to identify midpoint)
frameWidth = 1920
frameCenter = frameWidth / 2
# desired target size (will adjust speed to try to maintain this)
desiredTarget = 510
# sets desired default speed
defaultSpeed = 45
# will store the most recent set speed here
currentSpeed = 0

# adjusts turning based on location of midpoint in frame
def directionControl(midpoint):
    if(int(midpoint[0]) > frameCenter):
        # turn right
        servo.setServoPulsewidth(1700)
    elif(int(midpoint[0]) < frameCenter):
        # turn left
        servo.setServoPulsewidth(1400)
    else: # go straight
        servo.setServoPulsewidth(1550)
    return 1
    
    
# adjusts speed based on size of target
def speedControl(coord1, coord2):
    # calculate actual target size
    targetSize = ((int(coord2[0]) - int(coord1[0]))**2 + (int(coord2[1]) - int(coord1[1]))**2)**0.5
    print("Target size = " + str(targetSize))    
    #adjust based on desired target size
    if(targetSize < desiredTarget):
        # speed up
        print("Speed up!")
        motors.setSpeeds(defaultSpeed + 10, defaultSpeed + 10)
        currentSpeed = defaultSpeed + 10
        print("CurrentSpeed: " + str(currentSpeed))
    elif(targetSize > desiredTarget):
        # slow down
        print("Slow down!")
        motors.setSpeeds(defaultSpeed - 10, defaultSpeed - 10)
        currentSpeed = defaultSpeed - 10
        print("CurrentSpeed: " + str(currentSpeed))
    else:
        print("!!! Ideal speed !!!")
        motors.setSpeeds(defaultSpeed, defaultSpeed)
    return 1

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
                    
                    if(decoded=="stop"):
                        # stop the TOAD
                        motors.setSpeeds(0,0)
                        motors.forceStop()
                        stop = 1
                    elif("NaN" in decoded):
                        # continue at the most recent speed/direction
                        print("NaN, maintaining speed...")
                        print("CurrentSpeed: " + str(currentSpeed))
                       # motors.setSpeeds(currentSpeed,currentSpeed)
                        
                    else:
                        # get coordinates from decoded string:
                        decoded = decoded[1:-1].split(")(") # remove parantheses, split into list of pairs
                        center = decoded[0].split(",")
                        corner1 = decoded[1].split(",")
                        corner2 = decoded[2].split(",")
                        
                        # FUNCTION CALLS HERE
                        directionControl(center)
                        speedControl(corner1, corner2)
                        
                    
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
    except KeyboardInterrupt: 
        motors.setSpeeds(0,0)
        sys.exit(0)
    finally:
        s.close()
