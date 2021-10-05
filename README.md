# Networks Projects

The repository contains the few python programs from CSOC3603 class

- Web Server
  - A simple multithreaded HTTP server written from scratch using python `socket` module
  - It serves any files in a directory over a network, defaulting to index.html. May improve at some point with a directory listing (à la Nginx)
- UDP Pinger
  - A implementation of the common `ping` program using UDP sockets. It requires a "server" program be listening for the ping messages on port `12000`
  - Outputs ping statistics and RTT