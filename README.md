iot-concepts
========

test various aspects of internet of things using MQTT, Arduino, Raspi, etc. Also my first git repository.

The whole things is described here: [Article on the Bouvet blog](http://blogg.bouvet.no/2014/03/10/an-internet-of-things-demo-using-raspberry-pi-arduino-minecraft-and-mqtt)

You need:
ScriptCraft (A bukkit plugin to Minecraft capable of running JavaScript)
Arduino
MQTT 


This code is hastily written for fun. I am a rookie at Arduino, Python and JavaScript. "Code that was written by assumption and works by coincidence"

Everything is (c) Simen Sommerfeldt licensed under CC-BY-SA (Creative commons by attribution)

What it does:
* Makes a skull move and laugh viciously if one passes a sonar with less than 40 cm. [Video](http://www.youtube.com/watch?v=QVhjefwIaoI)   
* Has the skull follow player movements and light eyes in Minecraft: [Video](http://www.youtube.com/watch?v=rR05VC3vPI0)

You need an MQTT broker (I use mosquitto) and install the library for it on the computer which is attached to the Arduino. I use a mac to run minecraft, and a RasPi to run the mosquitto broker and control the Arduino.

I use this repository to keep files in sync between the raspi and the mac


