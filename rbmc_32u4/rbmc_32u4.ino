#include <Wire.h>
#include <Keyboard.h>
#define SLAVE_ADDRESS 0x04

/*
  4-bit output pins:
  6, 7, 8 and 9.
  
  6 = power button
  7 = reset button
  8, 9 = undefined
  
  The LSB is:
  6
*/

unsigned char outputPins[4] = {6, 7, 8, 9};

/* 
 Pin assignments, using board:
 rbmc-x1

  ====Analog=====
  a0 = power led
  a1 = hdd led
  a2 = undefined
  a3 = undefined
  
  ====Digital====
  15 = undefined
  14 = undefined
  16 = undefined
  10 = undefined
  
  The LSB is: A0
*/
/*
 Specify the operating voltage of the board.
 By default, this should be 50 (50 * 100 mV = 5V)
 
 MappedValues represents actual ADC values.
 It is populated automatically.

 Define analog input pins below. By default the Pro Micro is equipped with 4:
 A0, A1, A2, and A3.

 Define the digital input pins below. By default, these are the pins right next to the analog inputs:
 15, 14, 16, and 10.
 
 */

int voltage = 50;
unsigned char mappedValues[4] = {};
unsigned char analoginPins[4] = {A0, A1, A2, A3};
unsigned char digitalinPins[4] = {15, 14, 16, 10};
unsigned char analogValues[4] = {19, 19, 19, 19};    
unsigned char senseBytes[8] = {};
unsigned int lastValue = 0;

int arraynumber = 0;
unsigned char bytes[8] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
int keyboardBytes = 0;
int keyboardPress = 0;


void setup() {
       
  // convert analogValues to arduino value out of 255
  
  for (int i=0; i<4; i++) {
    int temp = analogValues[i];
    mappedValues[i] = map(temp, 0, voltage, 0, 255);
  }
  
  // turn all output pins -> output
  for (int i=0; i<4; i++) {
    pinMode(outputPins[i], OUTPUT);
  }
  
  // turn all digital input pins -> input using internal pullups
  for (int i=0; i<4; i++) {
    pinMode(digitalinPins[i], INPUT);
  }
  
  // enable i2c slave
  Wire.begin(SLAVE_ADDRESS);
  
  // begin serial monitor for debug
  Serial.begin(115200);
  
  // on recieve when pi asks to set state on output pins
  Wire.onReceive(receiveEvent);
  
  // onrequest when pi asks arduino for pin states
  Wire.onRequest(RequestedEvent);
  
  // turn all pins low
  for (int i=0; i<4; i++) {
    digitalWrite(outputPins[i], HIGH);
  }

  Keyboard.begin();

  //pinMode(keyboardEnable,INPUT_PULLUP);
}

void loop() {
//I will leave this one empty for now.
}

void receiveEvent(int num) {
  
  // read 8 bits of data
  int x = Wire.read();
  //Serial.println("---------");
  Serial.println(x);
  //Serial.println("Previous keyboardBytes: " +String(keyboardBytes));
  
  //This is a procress when we know how many bytes we need to recieve after the data bytes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     ///
  if (keyboardBytes > 0) {
    // do the thing
    bytes[arraynumber] = x;
    arraynumber += 1;
    keyboardBytes -= 1;
        
    if (keyboardBytes == 0) {
      
      for (int i=0; i<keyboardPress; i++){
    
        //Serial.println("KeyboardData: " + String(bytes[i]));
        Keyboard.press(bytes[i]);
        Keyboard.releaseAll();
        }
        
        // clear
      for (int i=0; i<8; i++ ){
          bytes[i] = 0;
          //Serial.print(bytes[i]);
          //Serial.print(" ");
      }
      delay(250);
      Keyboard.releaseAll(); 
      keyboardPress = 0;
    }
    //Serial.println("Complete Returning");    
    arraynumber = 0;
    return;
  }

  //pin mode
  if (bitRead(x,7) == 0){
    Serial.println("PINMODE");
    int data = 0;
    int p = 1;
    int b = 0;
    int state = bitRead(x, 3);

    for (int i=0; i<3; i++) {
      b = i + 4;
      data += bitRead(x, b) * p;
      p = p * 2;
    }
    //Serial.print("state: " + String(state));
    //Serial.print("data: " + String(data));
   //Control the pin(Order of it)
   digitalWrite(outputPins[data], state);
  }
  
  //Keyboard mode
  if (bitRead(x,7) == 1){
    Serial.println("KeyboardMode!");
    int p = 1;
    for (int i=0; i<3; i++) {
      keyboardBytes += bitRead(x, i) * p;
      p = p * 2;
    }
  keyboardPress = keyboardBytes;  
  Serial.println("KeyboardBytes:" + String(keyboardBytes));
  }
}

// When the master requests data from the device, return the recieved values

void RequestedEvent() {
  
}  
