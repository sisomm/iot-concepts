//Accepts commands to control two LED's and two servos over the serial port. 
//This version uses the Softserial connection and Adafruit ServoShield 
//(c) Simen Sommerfeldt, @sisomm, simen.sommerfeldt@gmail.com Licensed as CC-BY-SA

//#include <Servo.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
//#include <SoftwareSerial.h>

const int bSize = 40; // Command Buffer size

const int ledPin0 = 12;          // the LEDS that control the eyes
const int ledPin1 = 13;;

// The code assumes that you have servos connected at position 0 and 1 for the skull (pan/tilt),
// and position 4 for the jaw

const int jawServo = 4;           // which servo controls the jaw
const int servo0Neutral = 350;    // My calibrated values for neutral positions
const int servo1Neutral = 320;


const int jawOpen=270;            // Values for the third servo that opens and closes the mouth
const int jawClosed=470;


Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(); // called this way, it uses the default address 0x40

const int nServos=16;
int lastServoPos[nServos];  // Array to remember the last servo positions

//SoftSerial to communicate with host over GPIO using pings 3,2
//SoftwareSerial mySerial(3, 2); // RX, TX

//Commands that are populated by the serialParser. Should be in an class 
String theCommand;
String arg1;
String arg2;
String arg3;


int serialParser(void) {    
  //Reads and parses commands from the serial port
  //The end of commmand token is '|', since the cr/lf is confusing on mac/raspi
  char buffer[bSize];  // Serial buffer
  char command[15];    // Arbitrary Value for command size
  char data1[15];      // ditto for data size
  char data2[15];
  char data3[15];
  int byteCount=0; // how many bytes that were read

  int finished=0;
  while(finished==0){
    char c = Serial.read();
    if(c>=0){
      if(c=='|' || byteCount==(bSize-1)) {
        finished=1;
        buffer[byteCount]=0;
      } else {
        buffer[byteCount++]=c;
      }
    }
  }
  
  if (byteCount  > 0) {          // Really simple parsing
    strcpy(command,strtok(buffer,","));
    strcpy(data1,strtok(NULL,","));             
    strcpy(data2,strtok(NULL,","));   
    strcpy(data3,strtok(NULL,","));   

    theCommand=String(command);
    arg1=String(data1);    
    arg2=String(data2);
    arg3=String(data3);  
    //mySerial.flush();

  }
  memset(buffer, 0, sizeof(buffer));   // Clear contents of Buffer

  return byteCount;
}


void setup() {
  Serial.begin(9600);
//  mySerial.begin(9600);

  pinMode(ledPin0,OUTPUT);
  pinMode(ledPin1,OUTPUT);
  
  lastServoPos[0]=servo0Neutral;
  lastServoPos[1]=servo1Neutral;

  pwm.begin();
  
  pwm.setPWMFreq(60);  // Analog servos run at ~60 Hz updates
  
}

void cmd_blink_times(int times){    // blinks the "eyes" during "speech"
  for(int i=1;i<=times;i++){
      digitalWrite(ledPin0,HIGH);
      digitalWrite(ledPin1,LOW); 
      delay(50);
      digitalWrite(ledPin0,LOW);
      digitalWrite(ledPin1,HIGH); 
      delay(50);
  }
  digitalWrite(ledPin1,LOW); 
}

void cmd_blink(){                  // default
  cmd_blink_times(9);
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

void cmd_jawPosition(int pos){    // moves the jaw in the skull to open (1) or shut(0)
  int thePosition;
  if(pos>0) {
    thePosition=jawOpen;
  } else {
    thePosition=jawClosed;
  }   
  pwm.setPWM(jawServo, 0, thePosition);
  lastServoPos[jawServo]=thePosition;
}


void cmd_jawMotion(int times, int do_blink){    // moves the jaw in the skull
  for(int i=1;i<=times;i++){
     pwm.setPWM(jawServo, 0, jawOpen);
     if(do_blink>0){
       cmd_blink_times(3);
     } else {
       delay(300);
     }
     pwm.setPWM(jawServo, 0, jawClosed);
     if(do_blink>0){
       cmd_blink_times(3);
     } else {
       delay(300);
     }
  }
  lastServoPos[jawServo]=jawClosed;
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
  //TODO make the code more robust and check for valid parameters

  if (serialParser() > 0) {
    if(theCommand.equalsIgnoreCase("LEDS_ON")){
      digitalWrite(ledPin0,HIGH); 
      digitalWrite(ledPin1,HIGH); 
    }
    else if(theCommand.equalsIgnoreCase("LEDS_OFF")){
      digitalWrite(ledPin0,LOW); 
      digitalWrite(ledPin1,LOW); 
    }
    else if(theCommand.equalsIgnoreCase("LED")){   
      int ledPin=ledPin0+arg1.toInt(); 
      int toState=arg2.toInt();
      cmd_led(ledPin, toState);
    }
    else if(theCommand.equalsIgnoreCase("BLINK")){   
      cmd_blink();
    }
    else if(theCommand.equalsIgnoreCase("JAW_MOTION")){    
      int times=arg1.toInt();
      int do_blink=arg2.toInt();
      cmd_jawMotion(times,do_blink);
    }
    else if(theCommand.equalsIgnoreCase("JAW_POSITION")){    
      int pos=arg1.toInt();
      cmd_jawPosition(pos);
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
    
    //these statements allow the host to understand that the command is finished
    Serial.println(theCommand);
//    mySerial.print(theCommand);
//    mySerial.print('\n');
//    mySerial.flush();
  }

}


