//Accepts commands to control two LED's and two servos over the serial port. 
//This version uses the Softserial connection and Adafruit ServoShield 
//(c) Simen Sommerfeldt, @sisomm, simen.sommerfeldt@gmail.com Licensed as CC-BY-SA

//#include <Servo.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <SoftwareSerial.h>


const int bSize = 40; // Command Buffer size

const int ledPin0 = 12;
const int ledPin1 = 13;
const int servoPin0= 9;
const int servoPin1= 10;


const int servo0Neutral = 350;    // My calibrated values for neutral positions
const int servo1Neutral = 320;

// called this way, it uses the default address 0x40
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

const int nServos=16;
int lastServoPos[nServos];

//SoftSerial

SoftwareSerial mySerial(3, 2); // RX, TX

//Commands

String theCommand;
String arg1;
String arg2;
String arg3;


char buffer[bSize];  // Serial buffer
char command[15];    // Arbitrary Value for command size
char data1[15];      // ditto for data size
char data2[15];
char data3[15];
int byteCount;

void SerialParser(void) {    
  //Reads and parses commands from the serial port
  //The end of commmand token is '|', since the cr/lf is confusing on mac/raspi

  byteCount = 0;
  int finished=0;
  while(finished==0){
    char c = mySerial.read();
    if(c>=0){
      if(c=='|'){ // || byteCount==(bSize-1)){
        finished=1;
        buffer[byteCount]=0;
      } else {
        buffer[byteCount++]=c;
      }
    }
  }
  //mySerial.print(buffer);
  Serial.print(buffer);
//  byteCount =  mySerial.readBytesUntil('\n',buffer,bSize);  

  if (byteCount  > 0) {          // Really simple parsing
    strcpy(command,strtok(buffer,","));
    strcpy(data1,strtok(NULL,","));             
    strcpy(data2,strtok(NULL,","));   
    strcpy(data3,strtok(NULL,","));   
  }
  memset(buffer, 0, sizeof(buffer));   // Clear contents of Buffer

  theCommand=String(command);
  arg1=String(data1);   // String versions of the arguments 
  arg2=String(data2);
  arg3=String(data3);  
  mySerial.flush();
}


void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);

  pinMode(ledPin0,OUTPUT);
  pinMode(ledPin1,OUTPUT);

  pwm.begin();
  
  pwm.setPWMFreq(60);  // Analog servos run at ~60 Hz updates
  
//  lastServoPos[0]=servo0Neutral;
//  lastServoPos[1]=servo1Neutral;  

}

void cmd_led(int ledPin, int toState){    // Set a led to a state
        char state;
      if(toState==1){          // Find out the desired state
        state=HIGH;
      } 
      else {
        state=LOW;
      }

      if (ledPin>ledPin1)
        Serial.println("Wrong LED pin argument");
      else{
        digitalWrite(ledPin,state); 
      } 
}

void cmd_servoSlow(int servoPin, int servoStart, int servoStop){  // move a servo from one pos to another
      lastServoPos[servoPin]=servoStop;

      if(servoStop>servoStart){
        for(int position=servoStart;position<servoStop;position+=2){
          pwm.setPWM(servoPin, 0, position);
          delay(20);
        }  
      } 
      else {
        for(int position=servoStart;position>servoStop;position-=2){
          pwm.setPWM(servoPin, 0, position);
          delay(20);
        }  
      }

}

void cmd_Servo(int servoPin,int servoPos){  // Set a servo to a position
        pwm.setPWM(servoPin, 0, servoPos);
        lastServoPos[servoPin]=servoPos;
}

void cmd_servosMove(int servo0To,int servo1To,int delayTime){    // Move the servos to a new position, remembering the old
                                                   // This commmand is special and works only on pins 0 and 1 as a pair. Change if other pins
      int increment0=(servo0To>lastServoPos[0]?+2:-2);
      int increment1=(servo1To>lastServoPos[1]?+2:-2);

      int repetitions=max(abs(servo0To-lastServoPos[0]),abs(servo1To-lastServoPos[1]))/2;  // We move servos two steps at a time
      //Serial.println(repetitions);
      for(int i=0;i<repetitions;i++){
        if(abs(servo0To-lastServoPos[0])>2){            // Stop moving the servo that has reached the position
          pwm.setPWM(0,0,lastServoPos[0]+=increment0);
        }
        if(abs(servo1To-lastServoPos[1])>2){
          pwm.setPWM(1,0,lastServoPos[1]+=increment1);        
        }
        delay(delayTime);    // Allow the move to complete
      }
}

void loop() {

  //Implements a ping-pong protocol with the other end. All commands must be acknowledged
  SerialParser();

  if (byteCount  > 0) {
    if(theCommand.equalsIgnoreCase("LEDS_ON")){
      digitalWrite(ledPin0,HIGH); 
      digitalWrite(ledPin1,HIGH); 
    }
    else if(theCommand.equalsIgnoreCase("LEDS_OFF")){
      digitalWrite(ledPin0,LOW); 
      digitalWrite(ledPin1,LOW); 
    }
    else if(theCommand.equalsIgnoreCase("LED")){   
      int ledPin=ledPin0+arg1.toInt(); // Find out which pin to control. 48 is the ascii code for '0'
      int toState=arg2.toInt();
      cmd_led(ledPin, toState);
    }
    else if(theCommand.equalsIgnoreCase("SERVO_SLOW")){    
      int servoPin=arg1.toInt();
      int servoStart=arg2.toInt();
      int servoStop=arg3.toInt();
      cmd_servoSlow(servoPin, servoStart, servoStop);
    }
    else if(theCommand.equalsIgnoreCase("SERVOS_MOVE")){    
      int servo0To=arg1.toInt();
      int servo1To=arg2.toInt();
      int delayTime=arg3.toInt();
      if (delayTime==0){
        delayTime=3;
      }
      cmd_servosMove(servo0To,servo1To,delayTime);
    }
    else if(theCommand.equalsIgnoreCase("SERVO")){   
      int servoPin=arg1.toInt();
      int servoPos=arg2.toInt();
      cmd_Servo(servoPin,servoPos);
    }
    else if(theCommand.equalsIgnoreCase("SERVO_NEUTRAL")){
      cmd_Servo(0,servo0Neutral);
      cmd_Servo(1,servo1Neutral);
    }
    Serial.println(theCommand);
    mySerial.print(theCommand);
    mySerial.print('\n');
    mySerial.flush();
  }

}


