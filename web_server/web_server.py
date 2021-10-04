"""
Student name: Jackson Miller
Course: COSC 3603 - Networks
Assignment: Web Server
Filename: web_server.py

Purpose: Make a multi-threaded Python web server using sockets

Input: See --help. Port and ip default to '0.0.0.0':80 and serves files from CWD

Output: Files served to a client browser

Assumptions: Many connections will not be made simultaneously

Limitations: Certainly not the most efficient or robust implementation.
             Only supports GET HTTP Method. Not securely using HTTPS.

Development Computer: Lenovo P73
Operating System: Windows 10 Pro
Interpreter: CPython 3.9.6
Integrated Development Environment (IDE): Visual Studio Code
Operational Status: Functional
"""
import argparse
import logging
import socket
import sys
import threading
import time
from pathlib import Path


def handle_client(client_socket: socket.socket, addr: str, dir: Path):
    """
    Function to handle individual handle client connections in seperate threads
    Parses the HTTP requests and serves the requested data back to the client, if available
    """

    HEADERS = "Server: Jank Python Server"

    message = client_socket.recv(1024).decode()
    # Parse request data, splitting on CRLF and <SPACE>
    request, *headers, data = message.split("\r\n")
    method, req_file, proto = request.split()

    # Log requests from the client
    logging.info("{}:{} -> {}".format(*addr, request))
    try:
        # Only listen to GET requests
        if method == "GET":
            # Serve index.html if root domain requested
            if req_file == "/":
                req_file = "/index.html"

            # Read binary data from requested file
            with open(Path(dir, req_file[1:]), "rb") as f:
                outputdata = f.read()

            # Send 200 status and headers
            client_socket.send(f"HTTP/1.1 200 OK\r\n{HEADERS}\r\n\r\n".encode())
        else:
            # We don't support any other methods for now
            client_socket.send("HTTP/1.1 405 Method Not Allowed".encode())
    except IOError:
        # If the requested file does not exist, return 404 status
        client_socket.send("HTTP/1.1 404 Not Found\r\n{HEADERS}]\r\n\r\n".encode())
        outputdata = (
            "<h2>404</h2>"
            f"<p>The file <em>{req_file}</em> does not exist on the server.</p>"
        ).encode()

    # Send data (file or 404) and close connection
    client_socket.send(outputdata)
    client_socket.close()


def start_server(server_sock: socket.socket, dir: Path):
    """Main Server runs in a dedicated thread to avoid blocking the original calling thread"""

    server_sock.listen(5)
    logging.info(
        "Server for {} listening at {}:{}".format(dir, *server_sock.getsockname())
    )
    while True:
        # Receive new clients and handle requests in seperate threads
        client_socket, addr = server_sock.accept()
        logging.info("New connection from {}:{}".format(*addr))
        # Daemon threads are used to ensure all threads are killed when the original one dies
        client = threading.Thread(
            target=handle_client, args=(client_socket, addr, dir), daemon=True
        )
        client.start()


def check_path(path: str) -> Path:
    """Helper function to verify directory argument"""
    dir = Path(path)
    if dir.exists and dir.is_dir():
        return dir.resolve()
    raise FileNotFoundError(path)


if __name__ == "__main__":
    """Program Entry Point"""
    # Setup logging
    logging.basicConfig(
        format="%(asctime)s|%(message)s", level=logging.INFO, datefmt="%H:%M:%S"
    )

    # Setup argument parsing
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--ip", default="0.0.0.0", help="IP address to listen on")
    p.add_argument("-p", "--port", type=int, default=80, help="Port to listen on")
    p.add_argument(
        "--dir",
        help="Directory to serve files from (default: CWD)",
        default=Path.cwd(),
        type=check_path,
    )
    args = p.parse_args()

    # Setup socket from the operating system
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((args.ip, args.port))

    # Server socket listens on dedicated thread to allow for quitting the server with CTRL-C
    # Unsure if there is a more standard way to do this
    try:
        server_thread = threading.Thread(
            target=start_server, args=(server_sock, args.dir), daemon=True
        )
        server_thread.start()

        # Simple infinite loop to keep the main thread alive until requested to quit
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        logging.info("Shutting down server...")
        server_sock.close()
    sys.exit(0)
