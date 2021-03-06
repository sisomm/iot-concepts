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
from video import create_capture
from common import clock, draw_str
import requests

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
    parser=argparse.ArgumentParser(prog="reportface.py")
    parser.add_argument('--cascade', help="Haar cascade file", default="haarcascade_frontalface_alt.xml")
    parser.add_argument('--nested_cascade', help="Inner Haar cascade file", default="haarcascade_eye.xml")
    parser.add_argument('--server', help="MQTT server", default="localhost")
    parser.add_argument('--topic', help="MQTT base topic path", default="/reportface/face/")
    parser.add_argument('--pause', type=int, help="Pause between captures in millis", default=0)
    parser.add_argument('--video_source', help="Camera index, file, or device", default="0")    
    parser.add_argument('--dropbox_token', help='Dropbox Access token ')
    parser.add_argument('--pushover_token', help='Pushover Access token ')
    parser.add_argument('--pushover_userkey', help='Pushover User Key ')
    options=parser.parse_args()

    if not options.dropbox_token or not options.pushover_token or not options.pushover_userkey:
        print('--tokens and keys are mandatory')
        sys.exit(2)

    try:
        video_src = int(options.video_source)
    except:
        video_src = options.video_source
 
    mypid = os.getpid()
    client = paho.Client("facedect_"+str(mypid))
    client.connect(options.server)
    topic = options.topic

    cascade = cv.CascadeClassifier(cv.samples.findFile(options.cascade))
    nested = cv.CascadeClassifier(cv.samples.findFile(options.nested_cascade))

    cam = create_capture(video_src, fallback='synth:bg={}:noise=0.05'.format(cv.samples.findFile('lena.jpg')))
    
    dbx = dropbox.Dropbox(options.dropbox_token)
    #initiate time variable so that we can get first face reported
    t_lastface= datetime.datetime(2009, 1, 6, 15, 8, 24, 0)
    sequencecounter=0
    while True:
        ret, img = cam.read()
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        gray = cv.equalizeHist(gray)

        #the sleep command eases the load
        if options.pause > 0:
            time.sleep(pause/1000)
        faces = detect(gray, cascade)
        vis = img.copy()
        draw_rects(vis, faces, (0, 255, 0))
        
        if  len(faces)>0:
            t_thisface=datetime.datetime.now()
            minutes = (t_thisface-t_lastface).total_seconds() /60
            t_lastface=t_thisface
            
            #save five images to dropbox, but only one notification per minute
            #print("Seqencecounter: "+str(sequencecounter))
            if minutes >= 1 or sequencecounter>0:
                
                timestring=t_thisface.strftime("%Y%m%d_%H%M%S_%f")[:-3]+"_"+str(sequencecounter)
                draw_str(img, (20, 20), "Simen Sommerfeldts door cam")
                
                cv.imwrite("/home/pi/face.jpg",img)
                f=open("/home/pi/face.jpg","rb")
                try: 
                   res=dbx.files_upload(f.read(),"/face"+"_"+timestring+".jpg",mode=WriteMode("overwrite"))                  
                except dropbox.exceptions.ApiError as err:
                    print('*** API error', err)
  
                print("Face at the door "+ timestring)
                
                if sequencecounter == 0 or minutes >=1: 

                    client.publish(topic,timestring)
                    r = requests.post("https://api.pushover.net/1/messages.json", data = {
                        "token": options.pushover_token,
                        "user": options.pushover_userkey,
                        "message": "Face at the door"
                    },
                    files = {
                        "attachment": ("image.jpg", open("/home/pi/face.jpg", "rb"), "image/jpeg")
                    })
                
                if sequencecounter < 4:
                    sequencecounter=sequencecounter+1
                else:
                    sequencecounter=0

        draw_str(vis, (20, 20), "Simen Sommerfeldts door cam")
        cv.imshow('Reportface', vis)

        if cv.waitKey(5) == 27:
            break
    cv.destroyAllWindows()
    client.disconnect()

