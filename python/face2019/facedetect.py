# face detection using haar cascades. Simens 2019 Edition with MQTT. Based on
# the examples that came with opencv

# Python 2/3 compatibility
from __future__ import print_function

import os, sys, time
import argparse
import numpy as np
import cv2 as cv
import paho.mqtt.client as paho

# local modules
from video import create_capture
from common import clock, draw_str


def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                     flags=cv.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv.rectangle(img, (x1, y1), (x2, y2), color, 2)

if __name__ == '__main__':
    import sys

    parser=argparse.ArgumentParser(prog="facedetect.py")
    parser.add_argument('--cascade', help="Haar cascade file", default="haarcascade_frontalface_alt.xml")
    parser.add_argument('--nested_cascade', help="Inner Haar cascade file", default="haarcascade_eye.xml")
    parser.add_argument('--server', help="MQTT server", default="localhost")
    parser.add_argument('--topic', help="MQTT base topic path", default="/raspberry/1/face/")
    parser.add_argument('--pause', type=int, help="Pause between captures in millis", default=0)
    parser.add_argument('--video_source', help="Camera index, file, or device", default="0")    
    options=parser.parse_args()

    try:
        video_src = int(options.video_source)
    except:
        video_src = options.video_source

    cascade_fn = options.cascade
    nested_fn  = options.nested_cascade
    server = options.server
    pause = options.pause
    
    mypid = os.getpid()
    client = paho.Client("facedect_"+str(mypid))
    client.connect(server)
    topic = options.topic

    cascade = cv.CascadeClassifier(cv.samples.findFile(cascade_fn))
    nested = cv.CascadeClassifier(cv.samples.findFile(nested_fn))

    cam = create_capture(video_src, fallback='synth:bg={}:noise=0.05'.format(cv.samples.findFile('lena.jpg')))

    totalTime=0.0
    iterations=0
    while True:
        ret, img = cam.read()
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        gray = cv.equalizeHist(gray)

    #the sleep command eases the load
        if pause > 0:
            time.sleep(pause/1000)
        t = clock()
        rects = detect(gray, cascade)
        vis = img.copy()
        draw_rects(vis, rects, (0, 255, 0))
        if not nested.empty():
            facenum=0
            for x1, y1, x2, y2 in rects:
                roi = gray[y1:y2, x1:x2]
                vis_roi = vis[y1:y2, x1:x2]
                subrects = detect(roi.copy(), nested)
                draw_rects(vis_roi, subrects, (255, 0, 0))
                
                midFaceX = x1+((x2-x1)/2)
                midFaceY = y1+((y2-y1)/2)
                facenum=facenum+1;
                client.publish(topic+str(facenum),str(midFaceX)+","+str(midFaceY),0)

                
        dt = clock() - t
        totalTime=totalTime+dt
        iterations=iterations+1
        draw_str(vis, (20, 20), 'time: %.1f ms' % (dt*1000))
        draw_str(vis, (20, 40), "Approved by KEITH, the friendly skull")
        cv.imshow('facedetect', vis)

        if cv.waitKey(5) == 27:
            break
    cv.destroyAllWindows()
    client.disconnect()
    print("Average execution time: %.1f " % ((totalTime/iterations)*1000))
