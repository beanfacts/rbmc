## Comms Documentation
`* = Planned`
## Introduction
This file documents the rBMC metadata exchange protocol as well as access methods. The described devices are as follows.  

The **system controller** is the main sense and control board in the rBMC system.  
It should be placed in the computer to be managed.  

The **cluster manager** controls multiple computers and acts as a reverse proxy* in order to allow multiple computers to be controlled from a single port, simplifying remote access.

Your computer is simply the device you will be using to access the web GUI.

At the moment, video streaming is of the mjpg format, though it is planned to change to WebSockets native video streaming in the future.
  
## rBMC Metadata Exchange Protocol (RMEP)

The websockets-based protocol is the method in which all devices exchange metadata. This includes locations and addresses of streams, for example.  
The computer or server specifies the purpose of the data it's sending, like keyboard input, which gets processed accordingly. The modes available are as follows. 


| Mode | Type | Purpose |
| ---- | ---- | ------- |
| list_src | Request - Response | Populate the list with available IP addresses of controllers | 
| change_src | Request - Response | List the available sources for a particular device. For instance, VNC and video, and where to find them. |
| integ_check | Request - Response | Check if the server is operational, by sending back the same input data |
| keyboard | Request | Send keystrokes to the system controller of specified name |
| control | Request | Send control signals to the system controller |
| sense | Request - Response | Read the state of inputs on the system controller |

---
---

## Cluster manager to system controller

| Protocol | Default Port | Purpose |
| -------- | ------------ | ------- |
| Websockets | 8001 | Metadata exchange |
| HTTP | 7070 | Video feed |
| RFB | 5500* | VNC connection |

#### RMEP examples

---
`keyboard`
```javascript
Request
{
    "mode": "keyboard", 
    "format": "arduino", 
    "keys": [129, 72], 
    "duration": 500
}

/* This combination presses Shift+H for 500ms. */
```
No response.

---

`control`
```javascript
Request
{
    "mode": "control",
    "pin": "power",
    "command": [true, 300, false]
}
/* This turns on the power pin, waits 300ms, then turns it off. */
```
No response.

---

`sense`
```javascript
Request
{
    "mode": "sense",
    "pins": ["power_led", "grid_supply", "digitalPin"],
}
```
```javascript
Response
{
    "voltageRef": 5000,
    "pins": {
        "power_led": 3100,
        "grid_supply": 1540,
        "digitalPin": false,
    },
    "success": true,
    "init_req": "list_src"
}
/*
voltageRef is the board's I/O voltage, in mV.
The pin values are the voltages on said pins, in mV.
Digital input pins will have a true/false value.
*/
```
---
---  

## Your computer to cluster manager

| Protocol | Default Port | Purpose |
| -------- | ------------ | ------- |
| Websockets | 8002 | Metadata exchange |
| HTTP | 80/443 | Web server (optional) |
| HTTP | 7070 | Video feed |
| RFB | 5500* | VNC connection |


#### RMEP examples
For these examples, the cluster manager address is `192.168.1.10`.  

---
`integ_check`  
```javascript
Request  > {"mode": "integ_check", "data": "3cd91d6a0d8fd"}
```
```javascript
Response > {"data": "3cd91d6a0d8fd", "success": true, "init_req": "integ_check"}
```
---
`list_src`
```javascript
Request  > {"mode": "list_src"}
```
```javascript
Response
{
    "sources": ["192.0.2.100", "192.0.2.101", "hostname"],
    "success": true,
    "init_req": "list_src"
}
```
---
`change_src`
```javascript
Request  > {"mode": "change_src", "source": "192.0.2.100"}
/* 
It should be noted with this example that the source is populated
with an IP address if the hostname is not specified, but this might
not necessarily be the actual IP address of the device! 
*/
```
```javascript
Response
{
    "hostname": "hello", 
    "video": {
        "url": "http://192.168.1.10:7070/stream/192-0-2-100/",
        "format": "mjpg"
    },
    "vnc": {
        "url": "http://192.168.1.10:7070/vnc/192-0-2-100/"
    }, 
    "source_ip": "192.0.2.100", 
    "proxy": true, 
    "success": true, 
    "init_req": "change_src"
}
/*
Returns the hostname and its internal IP address, as well as locations of video and VNC locations.

Proxy: true notifies the user that a proxy is in use for accessing the devices.
If a proxy is not used, the system controller in question must have an IP address
which is reachable from the user's network!
*/
```
*Assume the IP address of `hostname` is `192.0.2.102`*  
```javascript
Request  > {"mode": "change_src", "source": "hostname"}
/* View sources for the source named hostname */
```
```javascript
Response
{
    "hostname": "hostname", 
    "video": {
        "url": "http://192.168.1.10:7070/stream/192-0-2-102/",
        "format": "mjpg"
    }, 
    "vnc": {
        "url": "http://192.168.1.10:7070/vnc/192-0-2-102/"
    }, 
    "source_ip": "192.0.2.102", 
    "proxy": true, 
    "success": true,
    "init_req": "change_src"
}
/* This is the recommended method for extracting system controllers' IP addresses */
```
---
`keyboard`
```javascript
Request
{
    "mode": "keyboard",
    "format": "unicode",
    "keys": [16, 72],
    "duration": 500
}
/* 
This combination presses Shift+H for 500ms.
Translation to Arduino keycodes is performed in the broker.
*/
```
No response.

---

`control`
```javascript
Request
{
    "mode": "control",
    "pin": "power",
    "command": "press"
}
/* 
This tells the system controller to pull the pin high, wait 300ms, then pull the pin low,
or whatever defaults are programmed. This cannot be sent to the system controller so it is
translated at the cluster manager to its corresponding example.
*/

```
No response.

`sense`
No special cases for the sense function.
It uses the same syntax as the system controller example.

---
---


