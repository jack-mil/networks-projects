# udp_ping_server.py

"""
This server code was given as part of the assignment
"""

import random
import socket

# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Assign IP address and port number to socket
server_sock.bind(("", 12000))

while True:
    # Generate random number in the range of 0 to 10
    rand = random.randint(0, 10)
    # Receive the client packet along with the address it is coming from
    data, (ip, port) = server_sock.recvfrom(1024)
    print(f'Recieved "{data.decode()}" from {ip}:{port}')
    # Capitalize the message from the client
    data = data.upper()
    # If rand is less is than 4, we consider the packet lost and do not respond
    if rand < 4:
        continue
    # Otherwise, echo the data
    server_sock.sendto(data, (ip, port))
