#from http://cttoronto.com/03/11/2013/connection-and-communicating-arduino-and-raspberry-pi/ 

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# (c) Simen Sommerfeldt, @sisomm, simen.sommerfeldt@gmail.com Licensed as CC-BY-SA 
import os, serial, time
import argparse
import paho.mqtt.client as paho

parser = argparse.ArgumentParser()
parser.add_argument("-p","--port", help="The port where the Arduino is attached")
parser.add_argument("-s","--server", default="127.0.0.1", help="The IP address of the MQTT server")
parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1],  default=0,
                    help="increase output verbosity")
args = parser.parse_args()

remoteTopic="/arduino/2/remote"
sonarTopic="/arduino/2/sonar"

arduino = serial.Serial(args.port, 9600, timeout=1)
arduino.open()

def on_message(mosq, obj, msg):
    #called when we get an MQTT message that we subscribe to
    if(args.verbosity>0):
        print("Message received on topic "+msg.topic+" with payload "+msg.payload)


print("REPORTER: Connecting")
mypid = os.getpid()
client = paho.Client("arduino_report_"+str(mypid))
client.connect(args.server)
client.on_message = on_message

try:
    while True:
        response = arduino.readline()
        if(len(response)>0):
            if(args.verbosity>0):
                print("REPORTER: Arduino says:"+response.strip())
            if(response.startswith("Ping")):
                topic=sonarTopic
            else:
                topic=remoteTopic

            client.publish(topic,response.strip() ,0)

except KeyboardInterrupt:
    print "Interrupt received"
    arduino.close()
