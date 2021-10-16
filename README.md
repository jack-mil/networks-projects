# Networks Projects

The repository contains the few python programs from CSOC3603 class

- Web Server
  - A simple multithreaded HTTP server written from scratch using python `socket` module
  - It serves any files in a directory over a network, defaulting to index.html. May improve at some point with a directory listing (à la Nginx)
- UDP Pinger
  - A implementation of the common `ping` program using UDP sockets. It requires a "server" program be listening for the ping messages on port `12000`
  - Outputs ping statistics and RTT
- SMTP Client
  - Send an email by communicating with a mail server using the SMTP protocol. Any SMTP server could be used, I only got it to work with GMAIL using an app code instead of password (https://support.google.com/accounts/answer/185833)
