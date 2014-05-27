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
parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],  default=0,
                    help="increase output verbosity")
args = parser.parse_args()

arduino = serial.Serial(args.port, 9600)
arduino.setDTR(level=False)
mypid = os.getpid()
client = paho.Client("arduino_dispatch_"+str(mypid))

commands=Queue.Queue(0)

def on_message(mosq, obj, msg):
    #called when we get an MQTT message that we subscribe to
    #Puts the command in the queue

    if(args.verbosity>1):
        print("DISPATCHER: Message received on topic "+msg.topic+" with payload "+msg.payload)

    arduinoCommand=msg.payload
    commands.put(arduinoCommand)

def connectall():
    print("DISPATCHER: Connecting")
    arduino.open()
    client.connect(args.server)
    client.subscribe("/arduino/1/incoming", 0)
    client.on_message = on_message

def disconnectall():
    print("DISPATCHER: Disconnecting")
    arduino.close()
    client.unsubscribe("/arduino/1/incoming")
    client.disconnect()

def reconnect():
    disconnectall()
    connectall()

connectall()

try:
    while client.loop()==0:
        # Look for commands in the queue and execute them
        if(not commands.empty()):
            command=commands.get()
            if(args.verbosity>0):
                print("DISPATCHER: sending to Arduino: "+command)
            start=time.time()
            arduino.write(command+'|')

            # wait until we get OK back
            response=''
            ack=False
            while not ack:
                response=arduino.readline()
                if (len(response)>0):
                    ack=True

            end=time.time()
            print('Response {} to {} took {:G} millis'.format(response,command,(end-start)*1000))

except KeyboardInterrupt:
    print "Interrupt received"
    disconnectall()
