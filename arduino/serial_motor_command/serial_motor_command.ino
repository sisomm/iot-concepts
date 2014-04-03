//Motor control program
//Copied from http://arduino-info.wikispaces.com/SmallSteppers

/*Boiler code*/
/*-----( Import needed libraries )-----*/
#include <Stepper.h>

//---( Number of steps per revolution of INTERNAL motor in 4-step mode )---
#define STEPS_PER_MOTOR_REVOLUTION 32   

//---( Steps per OUTPUT SHAFT of gear reduction )---
#define STEPS_PER_OUTPUT_REVOLUTION 32 * 64  //2048  

//The pin connections need to be 4 pins connected
// to Motor Driver In1, In2, In3, In4  and then the pins entered
// here in the sequence 1-3-2-4 for proper sequencing
Stepper small_stepper(STEPS_PER_MOTOR_REVOLUTION, 8, 10, 9, 11);


/* Boiler code ends*/

int motorSpeed = 0;     //variable to set stepper speed                        

/* These variables are for the parser */

const int bSize = 40; // Command Buffer size
char buffer[bSize];  // Serial buffer
char command[15];    // Arbitrary Value for command size
char data1[15];      // ditto for data size
char data2[15];
char data3[15];
int byteCount;

String theCommand;
String arg1;
String arg2;
String arg3;

/* End of parser variables */

void cmd_motor(int spd, int steps2Take, int duration){
  small_stepper.setSpeed(spd);
  small_stepper.step(steps2Take);
  delay(duration);
}



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
  Serial.begin(9600);
}


void loop() {

  //Implements a ping-pong protocol with the other end. All commands must be acknowledged
  SerialParser();

  if (byteCount  > 0) {

    if(theCommand.equalsIgnoreCase("MOTOR")){   
      int spd=arg1.toInt(); // Find out which pin to control. 48 is the ascii code for '0'
      int steps2Take=arg2.toInt();
      int duration=arg3.toInt();
      cmd_motor(spd,steps2Take,duration);
    }

    Serial.println(theCommand);
  }

}


