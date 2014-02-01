# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# (c) Simen Sommerfeldt, @sisomm, simen.sommerfeldt@gmail.com Licensed as CC-BY-SA
import serial, time
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

def on_message(mosq, obj, msg):
    #called when we get an MQTT message that we subscribe to
    if(args.verbosity>0):
        print("Message received on topic "+msg.topic+" with payload "+msg.payload)

        arduinoCommand=msg.payload

    if(args.verbosity>0):
        print("sending to Arduino: "+arduinoCommand)
    arduino.write(arduinoCommand)

def connectall():
    print("Connecting")
    arduino.open()
    client.connect(args.server)
    client.subscribe("/arduino/1/incoming", 2)
    client.subscribe("/arduino/3/incoming", 2)
    client.on_message = on_message

def disconnectall():
    print("Disconnecting")
    arduino.close()
    client.unsubscribe("/arduino/1/incoming")
    client.unsubscribe("/arduino/3/incoming")
    client.disconnect()

def reconnect():
    disconnectall()
    connectall()

connectall()

#arduino.write('SERVO, 0, 50')
#arduino.write('SERVO, 1, 73')

try:
    while client.loop()==0:
        print('reading MQTT')
        now=time.time()
        connected=int(now-connect_time)
        print(connected)
        print('reading Arduiono')
        response = arduino.readline()
        if(len(response)>0):
            if(args.verbosity>0):
                print("Arduino says:"+response.strip())
            client.publish("/arduino/1/status",response.strip() ,0)

except IndexError:
    print "No data received within serial timeout period"
    disconnectall()

except KeyboardInterrupt:
    print "Interrupt received"
    disconnectall()

except RuntimError:
    print "uh-oh! time to die"
    disconnectall()

