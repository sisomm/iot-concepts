# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# (c) Simen Sommerfeldt, @sisomm, simen.sommerfeldt@gmail.com Licensed as CC-BY-SA

from threading import Timer
import time
import argparse,time
import pygame
import paho.mqtt.client as paho

parser = argparse.ArgumentParser()
parser.add_argument("-s","--server", default="127.0.0.1", help="The IP address of the MQTT server")
parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1],  default=0,
                    help="increase output verbosity")
args = parser.parse_args()

isBusy=False        # To make sure we only have one head movement active

def task_laugh():
    print("LAUGH")
    pygame.mixer.music.load("../sounds/witchlaugh.wav")
    pygame.mixer.music.play()
   
def task_goodbye():
    print("GOODBYE")
    pygame.mixer.music.load("../sounds/despicable.wav")
    pygame.mixer.music.play()

def task_hello():
    print("HELLO")
    pygame.mixer.music.load("../sounds/mday.wav")
    pygame.mixer.music.play()

def task_doh():
    print("DOH!")
    pygame.mixer.music.load("../sounds/doh.wav") 
    pygame.mixer.music.play()
def task_ledsOff():
    client.publish('/arduino/1/incoming','LEDS_OFF',2)

def task_ledsOn():
    client.publish('/arduino/1/incoming','LEDS_ON',2)

def task_turnHead():
    client.publish('/arduino/1/incoming','SERVO_SLOW, 1, 73, 170',2)

def task_turnHeadBack():
    client.publish('/arduino/1/incoming','SERVO_SLOW, 1, 170, 73',2)

def task_notBusy():
    global isBusy
    isBusy=False

def on_message(mosq, obj, msg):
    global isBusy
    if(msg.topic=='/raspberry/1/incoming'):
        print("Message received on topic "+msg.topic+" with payload "+msg.payload)
        if(msg.payload=="GOODBYE"):
            task_goodbye()

        if(msg.payload=="HELLO"):
            task_hello()

        if(msg.payload=="DOH"):
            task_laugh()

        if(msg.payload=="LAUGH"):
            task_laugh()

    if(msg.topic=='/arduino/2/sonar'):
        arguments=msg.payload.split(':');
        distance=int(arguments[1]);
        if(distance<40):
            if(isBusy): print('Sorry bussy scaring!')
            else:
                isBusy=True
                print('We turn skull')
                task_ledsOn()
                Timer(2,task_turnHead,()).start()
                Timer(6,task_laugh,()).start()
                Timer(8,task_turnHeadBack,()).start()
                Timer(9,task_ledsOff,()).start()
                Timer(12,task_notBusy,()).start()

client = paho.Client("halloween_broker")
client.connect(args.server)
connect_time=time.time()
client.on_message = on_message
client.subscribe('/arduino/2/sonar', 2)
client.subscribe('/raspberry/1/incoming',2)

pygame.mixer.init()
pygame.mixer.music.load("/home/pi/arduino/sounds/witchlaugh.wav")

try:
    while True:
        now=time.time()
        connected=int(now-connect_time)
        client.loop(300)

except KeyboardInterrupt:
    client.unsubscribe("/arduino/2/sonar")
    client.unsubscribe("/raspberry/1/incoming")
    client.disconnect()

