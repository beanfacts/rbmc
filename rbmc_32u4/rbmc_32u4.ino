#include <Wire.h>
#include <Keyboard.h>
#define SLAVE_ADDRESS 0x04

/*
  4-bit output pins:8 
  6, 7, 8 and 9.
  
  6 = power button
  7 = reset button
  8, 9 = undefined
  
  The LSB is:
  6
*/

unsigned char outputPins[4] = {6, 7, 8, 9};

/* 
 Pin assignments, using:
 rBMC System Controller C (Sparkfun Pro Micro)

  ====Analog=====
  a0 = power led
  a1 = hdd led
  a2 = undefined
  a3 = undefined
  
  The LSB is: A0
*/

/*
 Specify the operating voltage of the board.
 By default, this should be 50 (50 * 100 mV = 5V)

 Define analog input pins below. By default the Pro Micro is equipped with 4:
 A0, A1, A2, and A3.
 
*/

int byte_index = 0;

int keyboardBytes = 0;
int keyboardPress = 0;
int voltage = 50;

unsigned char bytes[8] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
unsigned char debug[8] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
volatile int allowed_control[2] = {8, 10};
unsigned char inputPins[4] = {A0, A1, A2, A3};
unsigned char mappedValues[4] = {};
unsigned char senseBytes[8] = {};
unsigned int lastValue = 0;

volatile int data[6] = {0, 0, 0, 0, 0, 0};
volatile int flag = 0;
volatile int debug_num = 0;

volatile int pinNum = 0;
volatile int pinState = 0;
volatile int reqState = 0;

volatile int x = 0;
volatile int mul = 0;
volatile int iic = 0;

volatile int sensePin = 0;

#define enablePin 4

void setup() {

  // begin serial monitor for debug
  Serial.begin(38400);
  
  // Never run if the programming mode is active.
  pinMode(4, INPUT_PULLUP);
  
  if (digitalRead(enablePin) == LOW) {
    delay(1000);
    Serial.println("Taking control of USB port.");
    Keyboard.begin();
  } else {
    delay(2000);
    Serial.println("To exit programming mode, turn off the KB pin.");
    while (true) {
      delay(1000);
      Serial.println("<PROGRAM MODE> Waiting..");
    }
  }


       
  // turn all output pins -> output
  for (int i=0; i<4; i++) {
    pinMode(outputPins[i], OUTPUT);
  }

  // turn all pins low
  for (int i=0; i<4; i++) {
    digitalWrite(outputPins[i], LOW);
  }
  
  // enable i2c slave
  Wire.begin(SLAVE_ADDRESS);
  
  // on recieve when pi asks to set state on output pins
  Wire.onReceive(receiveEvent);
  
  // onrequest when pi asks arduino for pin states
  Wire.onRequest(requestEvent);

}

void loop() {
  
  delay(100);

  if (flag == 1) {

    Serial.print("dbg# = ");
    Serial.println(debug_num);
    
    for (int i=0; i < 6; i++) {
      /* Ignore non-printing characters */

      volatile bool ok = false;

      if (data[i] > 31) {
        ok = true;
      } else {
        for (int i = 0; i < sizeof(allowed_control); i++) {
          if (allowed_control[i] == data[i]) {
            ok = true;
            break;
          }
        }
      }

      
      if (ok == true) {
        Keyboard.press(data[i]);
        Serial.print(data[i]);
        Serial.print(" pressed ");
      } else {
        Serial.print(data[i]);
        Serial.println(" ignored ");
      }
    }

    for (int i=0; i < 6; i++) {
      data[i] = 0;
    }

    delay(5);
    Keyboard.releaseAll();

    flag = 0;
    
  } else if (flag == 2) {
    
    Serial.print("f: 2");
    
    pinState = bitRead(iic, 7);
    reqState = bitRead(iic, 6);

    if (pinState + reqState == 2) {
      
      sensePin = iic - 192;
      Serial.print("SensePin = ");
      Serial.println(sensePin);
    
    } else {
      
      if (pinState == 1) {
        pinNum = iic - 128;
      } else {
        pinNum = iic;
      }
      
      if (pinNum < 4) {
        digitalWrite(outputPins[pinNum], pinState);
      }
      
    }
    
    flag = 0;
    
  }
  
}

void receiveEvent(int num) {

  debug_num = num;
  flag = 0;
  x = 0;

  if (num > 1) { 
    
    volatile int i = 0;
    
    while (Wire.available()) {
      x = Wire.read();
      data[i] = x;
      i++;
    }

    flag = 1;

  } else {

    iic = Wire.read();
    flag = 2;
    
  }

}

void requestEvent() {
  volatile int resp = analogRead(inputPins[sensePin]);
  resp = map(resp, 0, 1023, 0, 255);
  Wire.write(resp);
  sensePin = 0; 
}  
