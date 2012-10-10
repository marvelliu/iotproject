#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os,xmpp,time,select,datetime
import serial

reload(sys) 
sys.setdefaultencoding('utf-8') 
  

#class Bot:
#  
#    def __init__(self, jabber, thisjid, remotejids, serverinfo):
#        self.jabber = jabber
#        self.thisjid = thisjid

def read_brightness():
    ttydev = '/dev/ttyACM0' 
    rate = 9600
    try:
        ser = serial.Serial(ttydev, baudrate=rate)
        sys.stdout.write("%s\n%s\n"%(ser.name,ser.baudrate))
        time.sleep(2)
        ser.write("LIGHT")
        time.sleep(0.1)
        t = ser.readline()
        v = float(t)
        time.sleep(0.1)
        ser.close()
        return 1, v
    except serial.serialutil.SerialException,e:
        return -1, str(e)

def get_brightness_description(v):
    result = ""
    if v<5:
        result = u"伸手不见五指.."
    elif v<100:
        result = u"台灯水平吧.."
    elif v<900:
        result = u"阴天水平吧.."
    elif v>=1023:
        result = u"溢出了，太阳真大.."
    elif v>=950:
        result = u"%s, 太阳真大，今儿天气不错"%v
    else:
        result = v
    return result

def read_temperature():
    ttydev = '/dev/ttyACM0' 
    rate = 9600
    try:
        ser = serial.Serial(ttydev, baudrate=rate)
        sys.stdout.write("%s\n%s\n"%(ser.name,ser.baudrate))
        time.sleep(2)
        ser.write("TEMP")
        time.sleep(0.1)
        t = ser.readline()
        v = float(t)
        time.sleep(0.1)
        ser.close()
        return 1, v
    except serial.serialutil.SerialException,e:
        return -1, str(e)

