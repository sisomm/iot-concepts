# Post faces to dropbox. Intended to function as door watch 
# face detection using haar cascades. Simens 2019 Edition with MQTT. Based on
# the examples that came with opencv

import os, sys, datetime
import argparse
import numpy as np
import cv2 as cv
import paho.mqtt.client as paho
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

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
    TOKEN=''

    parser=argparse.ArgumentParser(prog="reportface.py")
    parser.add_argument('--cascade', help="Haar cascade file", default="haarcascade_frontalface_alt.xml")
    parser.add_argument('--nested_cascade', help="Inner Haar cascade file", default="haarcascade_eye.xml")
    parser.add_argument('--server', help="MQTT server", default="localhost")
    parser.add_argument('--topic', help="MQTT base topic path", default="/reportface/face/")
    parser.add_argument('--pause', type=int, help="Pause between captures in millis", default=0)
    parser.add_argument('--video_source', help="Camera index, file, or device", default="0")    
    parser.add_argument('--token', help='Access token ')
    options=parser.parse_args()

    if not options.token:
        print('--token is mandatory')
        sys.exit(2)

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
    
    dbx = dropbox.Dropbox(options.token)
    #initiate time variable so that we can get first face reported
    t_lastface= datetime.datetime(2009, 1, 6, 15, 8, 24, 0)

    while True:
        ret, img = cam.read()
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        gray = cv.equalizeHist(gray)

        #the sleep command eases the load
        if pause > 0:
            time.sleep(pause/1000)
        rects = detect(gray, cascade)
        vis = img.copy()
        draw_rects(vis, rects, (0, 255, 0))
        
        if  len(rects)>0:
            t_thisface=datetime.datetime.now()
            minutes = (t_thisface-t_lastface).total_seconds() /60
            t_lastface=t_thisface
            if minutes >= 1:
                timestring=t_thisface.strftime("%Y%m%d_%H%M%S")
                client.publish(topic,timestring)
                print("Face at the door")
                cv.imwrite("/home/pi/face.jpg",img)
                f=open("/home/pi/face.jpg","rb")
                try: 
                   res=dbx.files_upload(f.read(),"/face"+"_"+timestring+".jpg",mode=WriteMode("overwrite"))                  
                except dropbox.exceptions.ApiError as err:
                    print('*** API error', err)

                print('uploaded as', res.name.encode('utf8'))

        draw_str(vis, (20, 20), "Simen Sommerfeldt")
        cv.imshow('Reportface', vis)

        if cv.waitKey(5) == 27:
            break
    cv.destroyAllWindows()
    client.disconnect()

