import socket
import time

HOST = '192.168.4.1'    # The remote host 
PORT = 2022             # The same port as used by the server

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print("Connecting...")
s.connect(HOST,PORT)
print("Success, sending payload")

for i in range(30):
    message = "Data Frame: " + str(i)
    s.send(message)
    time.sleep(1)

print("Completed Payload")