javac -cp RXTXcomm.jar SerialClass.java
javac -cp mqtt-client-0.4.0.jar:RXTXcomm.jar -sourcepath . Dispatcher.java
jar -cvf utils.jar SerialClass.class mqtt-client-0.4.0.jar RXTXcomm.jar 


