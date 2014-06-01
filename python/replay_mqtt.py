# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# (c) Simen Sommerfeldt, @sisomm, simen.sommerfeldt@gmail.com Licensed as CC-BY-SA 
import os, time
import argparse
import paho.mqtt.client as paho

parser = argparse.ArgumentParser()
parser.add_argument("-s","--server", default="127.0.0.1", help="The IP address of the MQTT server")
parser.add_argument("-f","--file", default="", help="the file of MQTT messages")
args = parser.parse_args()

print("MQTT_REPLAY: Connecting")
mypid = os.getpid()
client = paho.Client("mqtt_replay_"+str(mypid))
client.connect(args.server)

try:
    f=open(args.file,"r")
    for line in f:
        print line
        row=line.split('|')
        print row[0]
        print row[1]
        print row[2]
        time.sleep(float(row[0]))
        print('publishing {} to topic {}'.format(row[2],row[1]))
        client.publish(row[1],row[2].strip('\n'),0)
    f.close()

except KeyboardInterrupt:
    print "Interrupt received"
