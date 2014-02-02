//Accepts commands to control two LED's and two servos over the serial port. 

#include <Servo.h>

const int bSize = 30; // Command Buffer size

const int ledPin0 = 12;
const int ledPin1 = 13;
const int servoPin0= 9;
const int servoPin1= 10;

const int servo0Neutral = 65;    // My calibrated values for neutral positions
const int servo1Neutral = 72;

Servo servo0;
Servo servo1;

int lastServo0Pos=0;
int lastServo1Pos=0;

String theCommand;
String arg1;
String arg2;
String arg3;


char buffer[bSize];  // Serial buffer
char command[10];    // Arbitrary Value for command size
char data1[15];      // ditto for data size
char data2[15];
char data3[15];
int byteCount;

void SerialParser(void) {    
  //Reads and parses commands from the serial port

  byteCount = -1;
  byteCount =  Serial.readBytesUntil('\n',buffer,bSize);  

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

  Serial.flush();
}


void setup() {
  Serial.begin(57600);

  pinMode(ledPin0,OUTPUT);
  pinMode(ledPin1,OUTPUT);

  servo0.attach(servoPin0);
  servo1.attach(servoPin1);

  // move servo to neutral position
  servo0.write(servo0Neutral); 
  servo1.write(servo1Neutral);

  lastServo0Pos=servo0Neutral;
  lastServo1Pos=servo1Neutral;  

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
        //Send status back
        Serial.print("Pin: ");
        Serial.print(ledPin);
        Serial.print(", State: ");
        Serial.println(state==HIGH?"HIGH":"LOW");
      }
}

void cmd_servoSlow(int servoPin, int servoStart, int servoStop){  // move a servo from one pos to another
      Servo theServo;
      if(servoPin==0) {
        theServo=servo0;
        lastServo0Pos=servoStop;
      }
      else {
        theServo=servo1;
        lastServo1Pos=servoStop;
      }
      if(servoStop>servoStart){
        for(int position=servoStart;position<servoStop;position+=2){
          theServo.write(position);
          delay(20);
        }  
      } 
      else {
        for(int position=servoStart;position>servoStop;position-=2){
          theServo.write(position);
          delay(20);
        }  
      }

      // Send status back  
      Serial.print("Servo slow: ");
      Serial.print(servoPin);
      Serial.print(", From: ");
      Serial.print(servoStart);
      Serial.print(" to ");
      Serial.println(servoStop);
}

void cmd_Servo(int servoPin,int servoPos){  // Set a servo to a position
      if(servoPin==0){ 
        servo0.write(servoPos);
        lastServo0Pos=servoPos;
      }
      else{
        servo1.write(servoPos);
        lastServo1Pos=servoPos;
      }

      // Send status back  
      Serial.print("Servo: ");
      Serial.print(servoPin);
      Serial.print(", Position: ");
      Serial.println(servoPos);
}

void cmd_servosMove(int servo0To,int servo1To){    // Move the servos to a new position, remembering the old
      int increment0=(servo0To>lastServo0Pos?+2:-2);
      int increment1=(servo1To>lastServo1Pos?+2:-2);

      int repetitions=max(abs(servo0To-lastServo0Pos),abs(servo1To-lastServo1Pos))/2;  // We move servos two steps at a time
      
      for(int i=0;i<repetitions;i++){
        if(abs(servo0To-lastServo0Pos)>0){            // Stop moving the servo that has reached the position
          servo0.write(lastServo0Pos+=increment0);
        }
        if(abs(servo0To-lastServo0Pos)>0){
          servo1.write(lastServo1Pos+=increment0);        
        }
        delay(20);    // Allow the move to complete
      }

      // Send status back  
      Serial.print("Servos_move: ");
      Serial.print(lastServo0Pos);
      Serial.print(", ");
      Serial.println(lastServo1Pos);
}

void loop() {

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
      cmd_servosMove(servo0To,servo1To);
    }
    else if(theCommand.equalsIgnoreCase("SERVO")){   
      int servoPin=arg1.toInt();
      int servoPos=arg2.toInt();
      cmd_Servo(servoPin,servoPos);
    }
    else if(theCommand.equalsIgnoreCase("SERVO_NEUTRAL")){
      servo0.write(servo0Neutral); 
      servo1.write(servo1Neutral); 
    }
  }

}


