# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# (c) Simen Sommerfeldt, @sisomm, simen.sommerfeldt@gmail.com Licensed as CC-BY-SA
import time
import os
import argparse
import paho.mqtt.client as paho

parser = argparse.ArgumentParser()
parser.add_argument("-t","--topic", nargs="+", help="One or more MQTT topic")
parser.add_argument("-s","--server", default="127.0.0.1", help="The IP address of the MQTT server")

args = parser.parse_args()

mypid = os.getpid()
client = paho.Client("record_mqtt"+str(mypid))
previous=time.time()

def on_message(mosq, obj, msg):
    global previous
    now=time.time()
    print('{:G}|{}|{}'.format((now-previous),msg.topic,msg.payload))
    previous=now

def connectall(topics):
    client.connect(args.server)
    for thetopic in topics:
        client.subscribe(thetopic, 0)
    client.on_message = on_message

def disconnectall(topics):
    for thetopic in topics:
        client.unsubscribe(thetopic)
    client.disconnect()

connectall(args.topic)

try:
    while client.loop()==0:
        pass

except KeyboardInterrupt:
    disconnectall(args.topic)
