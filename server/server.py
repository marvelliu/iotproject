#!/usr/bin/env python
 
"""
A simple echo server (UDP)
"""
 
import socket
 
# define servr properties
#host = '192.168.1.201'
#host = '192.168.242.1'
host = ''
port = 8000
size = 1024
 
# configure server socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))
 
# wait for connections
# terminate with 
try:
  while True:
    print "recving..."
    data, address = sock.recvfrom(size)
    print "datagram from", address
    data = data + "\0"
    print data
    reply = "ack:"+ data
    sock.sendto(reply, address)
finally:
  sock.close()