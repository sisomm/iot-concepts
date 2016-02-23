#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time
import Queue
import os
import sys
import argparse
import paho.mqtt.client as paho
import RPi.GPIO as GPIO


# Initialise the PWM device using the default address
pwm = PWM(0x40)
# Note if you'd like more debug output you can instead run:
#pwm = PWM(0x40, debug=True)

jawServo=4
servo0Neutral=300
servo1Neutral=300

jawOpen=270
jawClosed=470

nServos=16
lastServoPos=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

#special considerations for servos 0 and 1
servoXMin=200 
servoXMax=520 
servoXMid=330
servoYMin=235
servoYMax=520
servoYMid=300 

def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolution
  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)

def on_message(mosq, obj, msg):
    #called when we get an MQTT message that we subscribe to
    #Puts the command in the queue

    if(args.verbosity>1):
        print("SERVOSHIELD: Message received on topic "+msg.topic+" with payload "+msg.payload)

    command=msg.payload
    parselist=command.split(',')
    commands.put(parselist)

def connectall():
    print("DISPATCHER: Connecting")
    client.connect(args.server)
    client.subscribe("/servoshield/1/incoming", 0)
    client.on_message = on_message

def disconnectall():
    print("DISPATCHER: Disconnecting")
    client.unsubscribe("/servoshield/1/incoming")
    client.disconnect()

def reconnect():
    disconnectall()
    connectall()

def servoMove(servo,position):
    pwm.setPWM(servo,0,position)
    lastServoPos[servo]=position

def servosNeutral():
    servoMove(0,servoXMid)
    servoMove(1,servoYMid)

def servosMove(servo0To, servo1To,delatyTime):
    if(servo0To>lastServoPos[0]):
        increment0=2
    else:
        increment0=-2

    if(servo1To>lastServoPos[1]):
        increment1=2
    else:
        increment1=-2

    repetitions=int(max(abs(servo0To-lastServoPos[0]),abs(servo1To-lastServoPos[1]))/2)
    for i in range(0,repetitions):
        if(abs(servo0To-lastServoPos[0])>2):
            servoMove(0,lastServoPos[0]+increment0)
        if(abs(servo1To-lastServoPos[1])>2):
            servoMove(1,lastServoPos[1]+increment1)
        print delatyTime
        time.sleep(delatyTime/1000)

def jawPosition(position):
    if(position==0):
        servoMove(jawServo,jawClosed)
    else:
        servoMove(jawServo,jawOpen)        

def jawMotion(times,doBlink):
    for i in range(times):
        jawPosition(1)
        if(doBlink==0):
            time.sleep(0.3)
        else:
            blink(3)
        
        jawPosition(0)
        if(blink==0):
            time.sleep(0.3)
        else:
            blink(3)

def led(led,onOff):
    if(led==0):
        pin=18
    else:
        pin=23

    if(onOff==0):
        state=GPIO.LOW
    else:
        state=GPIO.HIGH

    GPIO.output(pin,state)

def blink(times):
    for i in range(times):
        led(0,1)
        led(1,1)
        time.sleep(0.05)
        led(0,0)
        led(1,0)
        time.sleep(0.05)


parser = argparse.ArgumentParser()
parser.add_argument("-s","--server", default="127.0.0.1", help="The IP address of the MQTT server")
parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],  default=0,
                    help="increase output verbosity")
args = parser.parse_args()

mypid = os.getpid()
client = paho.Client("servoshield_dispatch"+str(mypid))

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)

commands=Queue.Queue(0)
connectall()
pwm.setPWMFreq(60)                        # Set frequency to 60 Hz
servosNeutral()

try:
    while client.loop()==0:
        # Look for commands in the queue and execute them
        if(not commands.empty()):
            action=commands.get()
            if(args.verbosity>0):
                print("DISPATCHER: sending to servoshield: "+action[0])
            if(action[0]=='SERVOS_NEUTRAL'):
                servosNeutral()
            elif(action[0]=='JAW_POSITION'):
                jawPosition(int(action[1]))
            elif(action[0]=='SERVOS_MOVE'):
                servosMove(int(action[1]),int(action[2]),int(action[3]))
            elif(action[0]=='JAW_MOTION'):
                jawMotion(int(action[1]),int(action[2]))
            elif(action[0]=='LEDS_ON'):
                led(0,1)
                led(1,1)
            elif(action[0]=='LEDS_OFF'):
                led(0,0)
                led(1,0)
            elif(action[0]=='BLINK'):
                blink(int(action[1]))

# except KeyboardInterrupt:
except:
    print "Interrupt received"
    print "Unexpected error:", sys.exc_info()[0]
    disconnectall()


