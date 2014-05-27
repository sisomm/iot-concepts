# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# (c) Simen Sommerfeldt, @sisomm, simen.sommerfeldt@gmail.com Licensed as CC-BY-SA

import os
import argparse,time
import pygame
import paho.mqtt.client as paho

parser = argparse.ArgumentParser()
parser.add_argument("-s","--server", default="127.0.0.1", help="The IP address of the MQTT server")
parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1],  default=0,
                    help="increase output verbosity")
args = parser.parse_args()

def task_laugh():
    pygame.mixer.music.load("../sounds/witchlaugh.wav")
    pygame.mixer.music.play()
   
def task_goodbye():
    pygame.mixer.music.load("../sounds/despicable.wav")
    pygame.mixer.music.play()

def task_hello():
    pygame.mixer.music.load("../sounds/mday.wav")
    pygame.mixer.music.play()

def task_doh():
    print("SOUNDPLAYER DOH!")
    pygame.mixer.music.load("../sounds/doh.wav") 
    pygame.mixer.music.play()

def on_message(mosq, obj, msg):

        print("SOUNDPLAYER: Message received on topic "+msg.topic+" with payload "+msg.payload)
        if(msg.payload=="GOODBYE"):
            task_goodbye()

        if(msg.payload=="HELLO"):
            task_hello()

        if(msg.payload=="DOH"):
            task_doh()

        if(msg.payload=="LAUGH"):
            task_laugh()

print("SOUNDPLAYER: Connecting")
mypid = os.getpid()
client = paho.Client("sound_broker_"+str(mypid))
client.connect(args.server)
connect_time=time.time()
client.on_message = on_message
client.subscribe('/raspberry/1/incoming',0)

pygame.mixer.init()

try:
    while client.loop()==0:
        pass

except KeyboardInterrupt:
    print('SOUNDPLAYER: Interrupt')
    client.unsubscribe("/raspberry/1/incoming")
    client.disconnect()

