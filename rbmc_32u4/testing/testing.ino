#include <Wire.h>
#define SLAVE_ADDRESS 0x04

void setup() {
  // enable i2c slave
  Wire.begin(SLAVE_ADDRESS);
  
  // begin serial monitor for debug
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
}
