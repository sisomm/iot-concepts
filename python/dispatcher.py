# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# (c) Simen Sommerfeldt, @sisomm, simen.sommerfeldt@gmail.com Licensed as CC-BY-SA
import serial, time
import Queue
import os
import argparse
import paho.mqtt.client as paho

parser = argparse.ArgumentParser()
parser.add_argument("-p","--port", help="The port where the Arduino is attached")
parser.add_argument("-s","--server", default="127.0.0.1", help="The IP address of the MQTT server")
parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1],  default=0,
                    help="increase output verbosity")
args = parser.parse_args()

arduino = serial.Serial(args.port, 57600, timeout=1)
mypid = os.getpid()
client = paho.Client("arduino_dispatch_"+str(mypid))

connect_time=time.time()

commands=Queue.Queue(0)

def sendToArduino(arduinoCommand):
    arduino.write(arduinoCommand)

    # wait until we get OK back
    ack=False
    response=''
    while not ack:
        time.sleep(0.10)
        response=arduino.readline()
        if len(response)>0):
            ack=True

        response=arduino.readline()
        if len(response)>0):
            ack=True
    return response



def on_message(mosq, obj, msg):
    #called when we get an MQTT message that we subscribe to
    if(args.verbosity>2):
        print("DISPATCHER: Message received on topic "+msg.topic+" with payload "+msg.payload)

    arduinoCommand=msg.payload

    commands.put(arduinoCommand)

    if(args.verbosity>0):
        print("DISPATCHER: sending to Arduino: "+arduinoCommand)

def connectall():
    print("DISPATCHER: Connecting")
    arduino.open()
    client.connect(args.server)
    client.subscribe("/arduino/1/incoming", 0)
    client.subscribe("/arduino/3/incoming", 0)
    client.on_message = on_message

def disconnectall():
    print("DISPATCHER: Disconnecting")
    arduino.close()
    client.unsubscribe("/arduino/1/incoming")
    client.unsubscribe("/arduino/3/incoming")
    client.disconnect()

def reconnect():
    disconnectall()
    connectall()

connectall()

try:
    while client.loop()==0:
        if(not commands.empty()):
            command=commands.get()
            print('Queue: '+command)
            response=sendToArduino(command) 
            print('Response: '+response)
        pass

except KeyboardInterrupt:
    print "Interrupt received"
    disconnectall()
