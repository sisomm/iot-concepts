//#include <IRremoteInt.h>
#include <IRremote.h>

int receiver = 11;

IRrecv irrecv(receiver);
decode_results results;
void setup(){
  Serial.begin(9600);
  irrecv.enableIRIn();
}

void loop(){
  if (irrecv.decode(&results)) {
//    if(results.value<0xFFFFFFFF){
 Serial.print("Remote: ");
    Serial.println (results.value, HEX);
    irrecv.resume();
  }
//  }
}

