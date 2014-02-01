iot-concepts
========

test various aspects of internet of things using MQTT, Arduino, Raspi, etc. Also my first git repository.

You need:
ScriptCraft (A bukkit plugin to Minecraft capable of running JavaScript)
Arduino
MQTT 


This code is hastily written for fun. I´ve had to change paradigms and languages so fast. And I
am a rookie at Arduino, Python and JavaScript. "Code that was written by assumption and works by coincidence"

Everything is (c) Simen Sommerfeldt licensed under CC-BY-SA (Creative commons by attribution)

Right now, it controls the power of two LED's using MQTT to send the status of levers to a Python script/arduino.

And makes a skull move and laugh viciously if one passes a sonar with less than 40 cm. [Video](http://www.youtube.com/watch?v=2eRPg_KQunU)  

You need an MQTT broker (I use mosquitto) and install the library for it on the computer which is attached to the Arduino. I use a mac to run minecraft, and a RasPi to run the mosquitto broker and control the Arduino.

I plan on documenting the whole thing in a blogpost. URL will be given here.

To test this, you need to position two levers attached to redstone lamps side by side in Minecraft, and not their positions. The positions are used to determine wich LED shall be ccontrolled. So you must edit the source accordingly

I use this repository to keep files in sync between the raspi and the mac. If you want to copy it: 
	Know that this is very much work in progress! 

