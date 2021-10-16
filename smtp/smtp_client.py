"""
Student name: Jackson Miller
Course: COSC 3603 - Networks
Assignment: SMPT Client
Filename: smtp_client.py

Purpose: Use the SMPT protocol and socket programming to communicate with an SMTP Server

Input: Email to send from, email of receiver

Output: Email is sent to specified address

Assumptions: Authentication on mail server to send email.
        See: https://support.google.com/accounts/answer/185833

Limitations: Mail server must allow authentication with base64 encoded
        username and password (or app code in the case of Google.)
        I could only get this to work with Gmail

Development Computer: Lenovo P73
Operating System: Windows 10 Pro
Compiler: Python 3.9.6
Integrated Development Environment (IDE): Visual Studio Code
Operational Status: Functional
"""
import argparse
import base64
import getpass
import json
import socket
import ssl

servers = {
    "GMAIL": ("smtp.gmail.com", 587),
    "OUTLOOK": ("smtp.office365.com", 587),
    "LETU": ("smtp.letu.edu", 587),
    "OTHER": None,
}

msg = (
    "From: From Person <from@fromdomain.com>\r\n",
    "To: To Person <to@todomain.com>\r\n",
    "MIME-Version: 1.0\r\n",
    "Content-type: text/html\r\n",
    "Subject: SMTP HTML e-mail test\r\n",
    "\r\n",
    "<p>This is an email message to be sent in HTML format.</p>\r\n",
    "<b>This is HTML in a message.</b>\r\n",
    "<h1>This is Header 1</h1>\r\n",
    "\r\n.",
)


class SMTP_Socket:
    """Wrapper class for TCP socket capable of upgrading to SSL connection"""

    def __init__(self, *args, **kwargs):
        """Create a socket using *args and **kwargs"""
        self.context: ssl.SSLContext = None
        self.sc = socket.socket(*args, **kwargs)

    def connect(self, address):
        """Wrapper for socket.socket.connect()"""
        self.sc.connect(address)
        recv = self.sc.recv(1024).decode()
        print(recv)
        if recv[:3] != "220":
            print("220 reply not received from server.")

    def close(self):
        """Wrapper for socket.socket.close()"""
        return self.sc.close()

    def send_msg(
        self, command: str, reply_code: str = "2", encode: bool = False
    ) -> str:
        """Send the SMTP command and print response"""
        if encode:
            # Hide passwords and encode in base64
            print(">", "*" * 10)
            command = base64.b64encode(command.encode()).decode() + "\r\n"
        else:
            command += "\r\n"
            print(f"> {command}")
        self.sc.send(command.encode())
        recv = self.sc.recv(1024).decode()
        if recv[: len(reply_code)] != reply_code:
            print(reply_code.ljust(3, "0"), "reply not received from server.")
        print(recv)
        return recv

    def enable_ssl(self, server_hostname: str):
        """Converts the wrapped socket to an SSL socket"""
        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.sc = self.context.wrap_socket(self.sc, server_hostname=server_hostname)


def parse_args() -> argparse.Namespace:
    """Parse args"""
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument(
        "--server", default="GMAIL", choices=servers, help="SMPT Server to connect to"
    )
    p.add_argument(
        "-f",
        "--file",
        type=argparse.FileType("r"),
        help='JSON file with "username" and "password" keys\n',
    )
    return p.parse_args()


def main(args: argparse.Namespace):
    """Main Program Body"""

    # Get server (and port) from args or input
    host = servers.get(args.server)
    if host is None:
        server, port = input(
            'Enter SMTP Server in the form "server.domain:port" > '
        ).split(":")
        port = int(port)
    else:
        server, port = host

    print(f"Connecting to {server}:{port}")

    smpt = SMTP_Socket(socket.AF_INET, socket.SOCK_STREAM)
    smpt.connect((server, port))

    # Send EHLO command and print server response.
    smpt.send_msg(f"EHLO {server}")

    #### AUTH AND LOGIN ####
    # Send STARTTLS command to server and print server response
    smpt.send_msg("STARTTLS")
    smpt.enable_ssl(server_hostname=server)

    smpt.send_msg(f"EHLO {server}")

    smpt.send_msg("AUTH LOGIN", "334")

    # Get auth from Json file or input()
    if f := args.file:
        account = json.load(f)
        username = account["username"]
        password = account["password"]
    else:
        username = input("Username: ")
        password = getpass.getpass("Password: ")

    # Send auth
    smpt.send_msg(username, "334", encode=True)
    smpt.send_msg(password, "235", encode=True)

    #### EMAIL ####
    # Send MAIL FROM command and print server response.
    mail_from = f"MAIL FROM:<{input('Enter sender address: ')}>"
    smpt.send_msg(mail_from)

    rcpt_to = f"RCPT TO:<{input('Enter receiver address: ')}>"
    smpt.send_msg(rcpt_to)

    # Send DATA command and print server response.
    smpt.send_msg("DATA", "354")
    smpt.send_msg("".join(msg))

    # Send QUIT command and get server response.
    smpt.send_msg("QUIT")

    # Close socket
    smpt.close()


if __name__ == "__main__":
    args = parse_args()
    main(args)
