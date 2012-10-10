#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os
import cv
import time
import os


reload(sys) 
sys.setdefaultencoding('utf-8') 
  
tmpimgfile = "/tmp/image.jpg"

def init_camera(tmpfile):
    global tmpimgfile
    print "Attempting to initalise webcam."
    camera = cv.CreateCameraCapture(0)
    cv.SetCaptureProperty(camera,cv.CV_CAP_PROP_FRAME_WIDTH, 384)
    cv.SetCaptureProperty(camera,cv.CV_CAP_PROP_FRAME_HEIGHT, 288)
    
    if not camera:
        print "Error opening WebCAM"
        return None 
    else:
        print "Webcam initalised."
    return camera

def release_camera(camera):
    del(camera)
    camera = None

def capture_loop(camera):
    while True:
        capture_camera(camera)
        time.sleep(0.3)

def capture_camera(camera):
    if camera == None:
        init_camera(tmpimgfile)
    global tmpimgfile
    if camera == None:
        return -1
    print "Capture started at "+time.asctime(time.localtime())
    frame = cv.QueryFrame(camera)
    if os.path.exists(tmpimgfile):
        os.remove(tmpimgfile)#remove previous file to ensure writing
    cv.SaveImage(tmpimgfile, frame)#save current frame
    print "writen"
    return 1
