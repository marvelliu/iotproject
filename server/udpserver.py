#!/usr/bin/python
# -*- coding: utf-8 -*-
 
 
import socket
import camera
import sys, os, datetime
import signal, threading
import serial
 
reload(sys) 
sys.setdefaultencoding('utf-8') 
 
glparams={}
cm=None

def handler(signum, frame):
    global cm,ser
    print "received signal %s"%signum
    if signum == signal.SIGTERM or signum == signal.SIGQUIT:
        sys.stdout.flush()
        sys.stderr.flush()
        release_camera(cm)
        ser.close()
        sig_exit()
        return None

signal.signal(signal.SIGINT,handler)
signal.signal(signal.SIGTERM,handler)
signal.signal(signal.SIGUSR1,handler)
signal.signal(signal.SIGQUIT,handler)

def getCameraData(cm):
    global glparams
    if camera.capture_camera(cm) < 0:
        return u'ack: 照相失败'
    f = open(glparams['tmp_image_file'], "rb")
    return f.read()

def processCarCtlData(data):
    global glparams
    p0 = data.find(":")
    p1 = data.find("&")
    p2 = data.find("*")
    dx = int(data[p0+1:p1])
    dy = int(data[p1+1:p2])
    dist = int(data[p2+1:])
    print "dx\t",dx,"\tdy",dy,"\tdist",dist
    sendCarCommand(dx, dy, dist)
    return "dx:%s\tdy:%s\tdist:%s"%(dx,dy,dist)

def initserial():
    ttydev = '/dev/ttyACM0' 
    rate = 9600
    try:
        ser = serial.Serial(ttydev, baudrate=rate)
    except serial.serialutil.SerialException,e:
        print str(e)
        sys.exit()
    return ser

def sendCarCommand(dx, dy, dist):
    global ser
    try:
        sys.stdout.write("CAR_XY:%s&%s*%s\n"%(dx,dy,dist))
        ser.write("CAR_XY:%s&%s*%s\n"%(dx,dy,dist))
        t = ser.readline()
        print t
    except serial.serialutil.SerialException,e:
        return -1, str(e)



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

    # configure server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print "server started %s:%s"%(host, port)
    cm = camera.init_camera(glparams['tmp_image_file'])
    print "camera initialized"

    ser=initserial()
     
    # wait for connections
    # terminate with 
    try:
      while True:
        print "recving..."
        data, address = sock.recvfrom(size)
        message = data + "\0"
        print "datagram from %s:\t%s"% (address, message)
        if message.startswith("sensor"):
#    print "sensor:",data
            reply = "ack:sensor data received"
        elif message.startswith("carctl"):
            reply = "carctl:"+processCarCtlData(data)
        elif message.startswith("camera"):
#            print "camera request"
            reply = "cmr:"+getCameraData(cm)
        else:
            reply = "ack:"+data
        sock.sendto(reply, address)
    finally:
      sock.close()
      ser.close()
      camera.release_camera(cm)


