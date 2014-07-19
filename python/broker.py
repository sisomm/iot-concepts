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
    global servoX, servoY # needs to be global because of delayed execution
    
    servoXMin=200 # 13 The commented numbers are for the old pan/tilt set
    servoXMax=520 # 133 
    servoXMid=360 # 73
    servoYMin=235 # 33
    servoYMax=520 # 80
    servoYMid=320 # 65
    
    l = []
    for t in msg.split(','):
        try:
            l.append(float(t))
        except ValueError:
            print('BROKER: Badly formed servo input')
            return 

#You need to adjust the code below to your own servo

    X=int(servoXMid-l[0]*180)        # Allow for calibration
    if(X<servoXMin):                 # The skull is heavy. not too big turns 
        servoX=servoXMin
    elif(X>servoXMax):
        servoX=servoXMax
    else:
        servoX=X

    Y=int(servoYMid-l[1]*180-20)     # I subtract 20 since the skull is mounted with a low pitch
    if(Y<servoYMin):                 # The skull is heavy. Not too big pitch
        servoY=servoYMin
    elif(Y>servoYMax):
        servoY=servoYMax
    else:
        servoY=Y

def ledCommand(command):
    print('BROKER: LED,'+command)
    client.publish('/arduino/1/incoming','LED,{}'.format(command),0)


def task_moveServos():
    print('BROKER: Move servos: {},{}'.format(servoY,servoX))
    client.publish('/arduino/1/incoming','SERVOS_MOVE,{},{},3'.format(servoX,servoY),0)

def task_laugh():
    print("BROKER: LAUGH")
    pygame.mixer.music.load("../sounds/witchlaugh.wav")
    pygame.mixer.music.play()
    task_jawMotion()
    task_jawMotion()
    task_ledsOn()
   
def task_goodbye():
    print("BROKER: GOODBYE")
    client.publish('/arduino/1/incoming','SERVO_NEUTRAL',0)
    pygame.mixer.music.load("../sounds/despicable.wav")
    pygame.mixer.music.play()
    task_jawMotion()

def task_hello():
    print("BROKER: HELLO")
    pygame.mixer.music.load("../sounds/mday.wav")
    pygame.mixer.music.play()
    task_jawMotion()
    task_jawMotion()
    task_ledsOn()

def task_doh():
    print("BROKER: DOH!")
    pygame.mixer.music.load("../sounds/doh.wav") 
    pygame.mixer.music.play()
    task_singleJawMotion()

def task_ledsOff():
    client.publish('/arduino/1/incoming','LEDS_OFF',0)

def task_ledsOn():
    client.publish('/arduino/1/incoming','LEDS_ON',0)

def task_turnLeft():
    client.publish('/arduino/1/incoming','SERVOS_MOVE, 520, 235, 7',0)

def task_turnRight():
    client.publish('/arduino/1/incoming','SERVOS_MOVE, 200, 235, 7',0)

def task_singleJawMotion():
    client.publish('/arduino/1/incoming','JAW_MOTION,1,1',0)

def task_jawMotion():
    client.publish('/arduino/1/incoming','JAW_MOTION,2,1',0)

def task_turnHeadBack():
    client.publish('/arduino/1/incoming','SERVOS_MOVE, 360, 320, 7',0)

def task_notBusy():
    global isBusy
    isBusy=False

def on_message(mosq, obj, msg):
    global isBusy       # Since we must queue some tasks these need to be global :-(
    global servoX
    global servoY

    if('lever' in msg.topic and not isBusy):
        if('249' in msg.topic):
            ledCommand('0,'+msg.payload)
        else:
            ledCommand('1,'+msg.payload)
            
    elif('skull' in msg.topic and not isBusy):
        if('ALONE' in msg.payload):
            task_goodbye()
            task_ledsOff()
        else:
            task_ledsOn()
            Timer(1,task_hello,()).start()

    elif('facetracker' in msg.topic and not isBusy):
        setServoCoords(msg.payload)
        task_moveServos()        

    elif('block' in msg.topic and not isBusy):
        task_doh()        


    elif(msg.topic=='/raspberry/1/incoming'):
        print("BROKER: Message received on topic "+msg.topic+" with payload "+msg.payload)
        if(msg.payload=="GOODBYE"):
            task_goodbye()

        if(msg.payload=="HELLO"):
            task_hello()

        if(msg.payload=="DOH"):
            task_doh()

        if(msg.payload=="LAUGH"):
            task_laugh()

    elif(msg.topic=='/arduino/2/sonar'):
        arguments=msg.payload.split(':');
        distance=int(arguments[1]);

        #Runs turns the head and laughs

        if(distance!=0 and distance<50):
            if(isBusy): print('BROKER: Sorry busy scaring!')
            else:
                isBusy=True
                print('BROKER: We turn skull')
                task_ledsOn()
                Timer(1,task_turnLeft,()).start()
                Timer(3,task_laugh,()).start()
                Timer(5,task_turnHeadBack,()).start()
                Timer(8,task_ledsOff,()).start()
                Timer(10,task_notBusy,()).start()

print("BROKER: Connecting")
mypid = os.getpid()
client = paho.Client("halloween_broker_"+str(mypid))
client.connect(args.server)
connect_time=time.time()
client.on_message = on_message
client.subscribe('/arduino/2/sonar', 0)
client.subscribe('/minecraft/+/sonar/#', 0)
client.subscribe('/minecraft/+/facetracker/#', 0)
client.subscribe('/minecraft/+/block/#', 0)
client.subscribe('/minecraft/+/skull/#', 0)
client.subscribe('/minecraft/+/lever/#', 0)
client.subscribe('/raspberry/1/incoming',0)

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
    client.unsubscribe('/minecraft/+/lever/#')
    client.unsubscribe('/raspberry/1/incoming')
    client.disconnect()

