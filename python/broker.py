# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# (c) Simen Sommerfeldt, @sisomm, simen.sommerfeldt@gmail.com Licensed as CC-BY-SA

from threading import Timer
import time
import os
import argparse,time
import pygame
import paho.mqtt.client as paho

parser = argparse.ArgumentParser()
parser.add_argument("-s","--server", default="127.0.0.1", help="The IP address of the MQTT server")
parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1],  default=0,
                    help="increase output verbosity")
args = parser.parse_args()

isBusy=False        # To make sure we only have one head movement active
servoX=0            # Where the servo is heading (used for queued tasks)
servoY=0

def setServoCoords(msg): #Parse the sinus values and populate servo values
    servoXMin=13;
    servoXMax=133;
    servoXMid=73;
    
    l = []
    for t in msg.split(','):
        try:
            print(t)
            l.append(float(t))
        except ValueError:
            print('BROKER: Badly formed servo input')
            return 

    X=int(l[0]*90)+90-17 #Allow for calibration
    if(X<servoXMin):
        servoX=servoXMin
    elif(X>servoXMax):
        servoX=servoXMax
    else:
        servoX=X

    servoY=int(l[1]*90)+90-17 #Allow for calibration
    
    print('BROKER: ServoX={}, ServoY={}'.format(servoX,servoY)) 

def task_laugh():
    print("BROKER: LAUGH")
    pygame.mixer.music.load("../sounds/witchlaugh.wav")
    pygame.mixer.music.play()
   
def task_goodbye():
    print("BROKER: GOODBYE")
    pygame.mixer.music.load("../sounds/despicable.wav")
    pygame.mixer.music.play()

def task_hello():
    print("BROKER: HELLO")
    pygame.mixer.music.load("../sounds/mday.wav")
    pygame.mixer.music.play()

def task_doh():
    print("BROKER: DOH!")
    pygame.mixer.music.load("../sounds/doh.wav") 
    pygame.mixer.music.play()

def task_ledsOff():
    client.publish('/arduino/1/incoming','LEDS_OFF',2)

def task_ledsOn():
    client.publish('/arduino/1/incoming','LEDS_ON',2)

def task_turnHead():
    client.publish('/arduino/1/incoming','SERVOS_MOVE, 50, 20',2)

def task_turnHeadBack():
    client.publish('/arduino/1/incoming','SERVOS_MOVE, 50, 72',2)

def task_notBusy():
    global isBusy
    isBusy=False

def on_message(mosq, obj, msg):
    global isBusy       # Since we must queue some tasks these need to be global :-(
    global servoX
    global servoY

    if('skull' in msg.topic and not isBusy):
        if('ALONE' in msg.payload):
            task_goodbye()
            task_ledsOff()
        else:
            task_hello()
            task_ledsOn()

    if('facetracker' in msg.topic and not isBusy):
        setServoCoords(msg.payload)

    if(msg.topic=='/raspberry/1/incoming'):
        print("BROKER: Message received on topic "+msg.topic+" with payload "+msg.payload)
        if(msg.payload=="GOODBYE"):
            task_goodbye()

        if(msg.payload=="HELLO"):
            task_hello()

        if(msg.payload=="DOH"):
            task_doh()

        if(msg.payload=="LAUGH"):
            task_laugh()

    if(msg.topic=='/arduino/2/sonar'):
        arguments=msg.payload.split(':');
        distance=int(arguments[1]);
        if(distance!=0 and distance<40):
            if(isBusy): print('BROKER: Sorry bussy scaring!')
            else:
                isBusy=True
                print('BROKER: We turn skull')
                task_ledsOn()
                Timer(2,task_turnHead,()).start()
                Timer(6,task_laugh,()).start()
                Timer(8,task_turnHeadBack,()).start()
                Timer(9,task_ledsOff,()).start()
                Timer(12,task_notBusy,()).start()

print("BROKER: Connecting")
mypid = os.getpid()
client = paho.Client("halloween_broker_"+str(mypid))
client.connect(args.server)
connect_time=time.time()
client.on_message = on_message
client.subscribe('/arduino/2/sonar', 2)
client.subscribe('/minecraft/+/sonar/#', 2)
client.subscribe('/minecraft/+/facetracker/#', 2)
client.subscribe('/minecraft/+/block/#', 2)
client.subscribe('/minecraft/+/skull/#', 2)
client.subscribe('/raspberry/1/incoming',2)

pygame.mixer.init()

try:
    while client.loop()==0:
        pass

except KeyboardInterrupt:
    print('BROKER: Interrupt')
    client.unsubscribe("/arduino/2/sonar")
    client.unsubscribe("/raspberry/1/incoming")
    client.unsubscribe('/minecraft/+/sonar/#')
    client.unsubscribe('/minecraft/+/facetracker/#')
    client.unsubscribe('/minecraft/+/block/#')
    client.unsubscribe('/minecraft/+/skull/#')
    client.unsubscribe('/raspberry/1/incoming')
    client.disconnect()

