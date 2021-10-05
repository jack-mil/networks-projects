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

Development Computer: Lenovo P73, RPI 4
Operating System: Windows 10 Pro, Manjaro Linux, Arch Linux (aarch64, RPI 4)
Interpretor: CPython 3.9.7
Integrated Development Environment (IDE): Visual Studio Code
Operational Status: Functional
"""

import socket
import time
from datetime import datetime
import argparse


# Contants used for argument parsing defaults. Overridden if arguments supplied
IP = "127.0.0.1"
PORT = 12000
COUNT = 10  # Number of pings to sent
TIMEOUT = 1  # Timeout in seconds

MESSAGE = "Ping {num} {time:%H:%M:%S}"  # Message template

def parse_args() -> argparse.Namespace:
    # Setup argument parsing
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("ip", nargs='?', default=IP, help="IP address to ping")
    p.add_argument("-p", "--port", type=int, default=PORT, help="Port on host to ping")
    p.add_argument("-c", "--count", type=int, default=COUNT, help="Number of packets to send")
    p.add_argument(
        "-t",
        "--timeout",
        default=TIMEOUT,
        type=float,
        help="Maximum seconds to wait for response",
    )
    return p.parse_args()

def main(ip: str, port: int, count: int, timeout: int):
    recv = 0  # Number of packets received
    times = []  # Record of RTTs

    # Setup socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)  # Configure packet timeout

    print(f"\nPinging {ip} with 16 bytes of data:")

    for seq in range(count):
        # Store the starting time
        start = time.perf_counter()

        # Format and send the message
        client_socket.sendto(
            MESSAGE.format(num=seq + 1, time=datetime.now()).encode(), (ip, port)
        )
        try:
            # Unpack the response
            data, (srv_ip, _) = client_socket.recvfrom(1024)

            # Calculate RTT
            end = time.perf_counter()
            rtt = (end - start) * 1000
            times.append(rtt)

            recv += 1
            print(f"Reply from {srv_ip}: data={data} time={rtt:.3f}ms")
        except socket.timeout:
            # If timeout while waiting for a response
            print("Request timed out")

    # Ensure socket is closed
    client_socket.close()

    # Format and print ping statistics
    # Same data as UNIX `ping` command
    print()
    print(f"Ping statistics for {ip}:")
    lost = count - recv
    print(
        "\tPackets: Sent = {}, Received = {}, Lost = {} ({:.1%} loss)".format(
            count, recv, lost, lost / count
        )
    )

    if len(times):
        print("Approximate round trip times in milli-seconds:")
    else:
        print(f"No response from server at {ip}")
        return

    print(
        "\tMinimum = {:.3f}ms, Maximum = {:.3f}ms, Average = {:.3}ms".format(
            min(times), max(times), sum(times) / len(times)
        )
    )


if __name__ == "__main__":
    """Program Entry Point"""
    args = parse_args()
    main(args.ip, args.port, args.count, args.timeout)
