#!/usr/bin/python
# -*- coding: utf-8 -*-
 
"""
A simple echo server (UDP)
"""
 
import socket
import camera
import sys, os, datetime
 
reload(sys) 
sys.setdefaultencoding('utf-8') 
 
glparams={}

def getCameraData(cm):
    global glparams
    if camera.capture_camera(cm) < 0:
        return u'ack: 照相失败'
    f = open(glparams['tmp_image_file'], "rb")
    return f.read()



if __name__ == '__main__':
    if os.access('config',os.R_OK):
        for ln in open('config').readlines():
            if not ln[0] in ('#',';'):
                key,val=ln.strip().split('=',1)
                if val[0]=='\'' and val[-1]=='\'':
                    val = val[1:-2]
                glparams[key.lower()]=val
    # define servr properties
    #host = '192.168.1.201'
    #host = '192.168.242.1'
    host = glparams['server'] 
    port = int(glparams['port'])
    size = int(glparams['buf_size'])

    print host
    print port 
    # configure server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print "server started"
    cm = camera.init_camera(glparams['tmp_image_file'])
    print "camera initialized"
     
    # wait for connections
    # terminate with 
    try:
      while True:
        print "recving..."
        data, address = sock.recvfrom(size)
        print "datagram from", address
        message = data + "\0"
        if message.startswith("sensor")>=0:
            print data
            reply = "ack: received"
        elif message.startswith("camera")>=0:
            reply = getCameraData(cm)
        else:
            reply = "ack:"+ data
        sock.sendto(reply, address)
    finally:
      sock.close()
      camera.release_camera(cm)


