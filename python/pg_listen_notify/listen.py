import os
import psycopg2
import paho.mqtt.client as paho
import select
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

connection = psycopg2.connect(
    dbname="simen",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
mypid=os.getpid()
client=paho.Client("postgres"+str(mypid))
client.connect("localhost")

cursor = connection.cursor()
cursor.execute("LISTEN notification;")

while True:
    if select.select([connection],[],[],5) == ([],[],[]):
        print("Timeout")
    else:
        connection.poll()
        while connection.notifies:
            notify = connection.notifies.pop(0)
            print(f"Got NOTIFY: {notify.pid}, {notify.channel}, {notify.payload}")
            client.publish("/postgres",notify.payload,0)
