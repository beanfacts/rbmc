# Tested compatible hardware/software

### Interfacing SBCs
- NanoPi Neo / Neo2; FriendlyCore
- Raspberry Pi Zero; Raspbian Stretch Lite
- Raspberry Pi 3B; Raspbian Stretch Desktop

General SBC Requirements
- 1GHz+ ARMv6+ processor
- 256MB+ memory
- I2C pins

### USB & I/O Microcontrollers
- Sparkfun Pro Micro
- Arduino Micro
- Arduino Due

Microcontroller Requirements
- Atmega 32u4 or SAMD based board supporting `Keyboard.h` libary
- Supported in Arduino IDE

Make sure you are using pin assignments that make sense for your particular board.

### Communication & Video Capture
USB Video 
- `ID 05e1:0408 Syntek Semiconductor Co., Ltd STK1160 Video Capture Device`  
- `ID 1b71:3002 Fushicai USBTV007 Video Grabber [EasyCAP]`
- `ID 534d:0021`  

I recommend setting your tv-norm to PAL if it's supported by your adapter.  
If it works with V4L, it should work with rbmc.

USB Ethernet 
- `ID 0fe6:9700 ICS Advent DM9601 Fast Ethernet Adapter`

Really any Ethernet adapter supported in the Linux kernel should work.

### Software

Python Interpreter  
- Python 3.5 and up.
- Requires `websockets` `smbus2`

Streaming Software  
- mjpg_streamer

Arduino IDE
- Requires Arduino 1.8+ if you plan to use the Arduino Due
