"""
Name: Jackson Miller
Course: COSC 3603 - Networks
Assignment: UDP Ping
Filename: udp_ping_client.py

Purpose: Implement a ping program simular to the `ping` utility on
         most operating systems

Input: Enter the IP and Port of the server to ping in the file. Run the program.

Output: Statistics about lost packets and round trip average time

Assumptions: Accompanying server program is listening on the remote ip and port

Limitations: IP and Port have to be specified in the client program

Development Computer: Lenovo P73
Operating System: Windows 10 Pro
Compiler: Python 3.9.7
Integrated Development Environment (IDE): Visual Studio Code
Operational Status: Functional
"""

import socket
import time
from datetime import datetime

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(1)  # One second timeout


IP = "127.0.0.1"
PORT = 12000

MESSAGE = "Ping {num} {time:%H:%M:%S}"  # Message template
COUNT = 10  # Number of pings to sent
TIMEOUT = 1  # Timeout in seconds

recv = 0  # Number of packets received
times = []  # Record of RTTs

print(f"\nPinging {IP} with 16 bytes of data:")

for seq in range(COUNT):
    # Store the starting time
    start = time.perf_counter()

    # Format and send the message
    client_socket.sendto(
        MESSAGE.format(num=seq + 1, time=datetime.now()).encode(), (IP, PORT)
    )
    try:
        # Unpack the response
        data, (ip, port) = client_socket.recvfrom(1024)

        # Calculate RTT
        end = time.perf_counter()
        rtt = (end - start) * 1000
        times.append(rtt)

        recv += 1
        print(f"Reply from {ip}: data={data} time={rtt:.3f}ms")
    except socket.timeout:
        # If timeout while waiting for a response
        print("Request timed out")

# Ensure socket is closed
client_socket.close()


# Format and print ping statistics
# Same data as UNIX `ping` command
print()
print(f"Ping statistics for {IP}:")
lost = COUNT - recv
print(
    "\tPackets: Sent = {}, Received = {}, Lost = {} ({:.1%} loss)".format(
        COUNT, recv, lost, lost / COUNT
    )
)
print("Approximate round trip times in milli-seconds:")
print(
    "\tMinimum = {:.3f}ms, Maximum = {:.3f}ms, Average = {:.3}ms".format(
        min(times), max(times), sum(times) / len(times)
    )
)
