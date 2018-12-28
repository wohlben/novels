import time
import socket

# creating a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local Host machine name
host = ""  # or just use (host == '')
port = 9999

# bind to pot
s.bind((host, port))

# Que up to 5 requests
s.listen(2)

connection_counter = 0
while True:
    # establish connection
    if connection_counter == 2:
        break
    clientSocket, addr = s.accept()
    print("got a connection from %s" % str(addr))
    currentTime = time.ctime(time.time()) + "\r\n"
    clientSocket.send(currentTime.encode("ascii"))
    clientSocket.close()
    connection_counter += 1
