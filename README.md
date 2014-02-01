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

What it does:
* Makes a skull move and laugh viciously if one passes a sonar with less than 40 cm. [Video](http://www.youtube.com/watch?v=2eRPg_KQunU)   
* Has the skull follow player movements and light eyes in Minecraft: [Video](http://www.youtube.com/watch?v=yu6P1Bz6P0c)

You need an MQTT broker (I use mosquitto) and install the library for it on the computer which is attached to the Arduino. I use a mac to run minecraft, and a RasPi to run the mosquitto broker and control the Arduino.

I plan on documenting the whole thing in a blogpost. URL will be given here.

I use this repository to keep files in sync between the raspi and the mac. If you want to copy it: 
	Know that this is very much work in progress! 



