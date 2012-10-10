#!/usr/bin/env python
 
"""
A simple echo server (UDP)
"""
 
import socket
import sys
 
# define servr properties
host = ''
#host = '192.168.1.201'
#host = '192.168.242.1'
port = 8000
size = 1024
 
# configure server socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
sock.listen(1)
 
# wait for connections
# terminate with 
while True:
    sys.stdout.write("listening\n")
    connection, client_address = sock.accept()
    print 'connection from %s\n', 
    print client_address
    
    sys.stdout.write("recving...\n")
    while True:
        data = connection.recv(size)
        if data:
            print 'received "%s"' % data
            data = data + "\0"
            if data.find("sensor")>=0:
                reply = "ack: received"
            else:
                reply = "ack:"+ data
            connection.sendall(reply)
        else:
            continue
sock.close()