#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os,xmpp,time,select
import pipes
import signal,os,sys,threading,time
import twitter,urllib2;
import serial
  


ttydev = '/dev/ttyACM0' 
rate = 9600


#os.system("/bin/stty -F %s raw speed 9600"%(ttydev))
ser = serial.Serial(ttydev, baudrate=rate)
print ser.name
print ser.baudrate
time.sleep(2)
#ser.write("TEMP")
ser.write("LIGHT")
time.sleep(0.1)
t = ser.readline()
print t
v = float(t)
print v
time.sleep(0.1)
ser.close()
