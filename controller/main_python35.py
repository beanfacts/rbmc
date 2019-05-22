#!/usr/bin/env python3

import asyncio, websockets
import ssl, pathlib
import json
import time

from smbus2 import SMBus, SMBusWrapper
bus_no = 0
iic = SMBus(bus_no)
address = 0x04

board_voltage = 5000

# Example list of sources for testing purposes
sources = \
    {
        "rBMC Demo Machine": {
            "hostname": "rbmc-target",
            "manage_ip": "192.168.1.122",
            "client_ip": "192.168.1.112",
            "video": {
                "url": "http://192.168.1.122:7070/?action=stream",
                "format": "mjpg",
            },  
            "vnc": {
                "url": False,
            }
        },
    }

respond = \
    {
        "change_src": True,
        "list_src": True,
        "integ_check": True,
        "get_addr": True,
        "keyboard": False,
	"sense": True,
	"control": False,
    }

output_assign = \
    {
        "power": 0,
        "reset": 1,
    }

input_assign = \
    {
        "power_led": 0,
        "hdd_led": 1,
    }

convert_keycode = \
    {
        # Modifiers
        16: 129,
        17: 128,
        9: 179,
        13: 10,
        27: 177,
        46: 212,

        # Arrow Keys
        37: 216,
        38: 218,
        39: 215,
        40: 217,
        
        # F keys
        112: 194,
        113: 195,
        114: 196,
        115: 197,
        116: 198,
        117: 199,
        118: 200,
        119: 201,
        120: 202,
        121: 203,
        122: 204,
        123: 205,
    }

"""
example_response = \
    {
        "mode": "integ_check",
        "success": True,
        "error_message": None,
        "data": "fbb2c776503c7",
    }
"""

@asyncio.coroutine
def err_json(mode, status, message):
    if status == False:
       print("Returning error") 
       return {"init_req": mode, "success": status, "error_message": message}

# Converting recieved string data to JSON format
@asyncio.coroutine
def preprocessor(message):
    try:
        formatted_message = json.loads(message)
        return formatted_message
    except json.decoder.JSONDecodeError:
        print("Server sent invalid data!")
        return {"error": "json decoder error"}

# Responding to client requests
@asyncio.coroutine
def responder(data):
    global sources
    mode = data["mode"]
    
    print("REQUEST  <<", data)
    print("Mode:", mode)

    if mode == "change_src":
        source_ip = data["source_ip"]
        try:
            resp = sources[source_ip]
            resp["source_ip"] = source_ip
        except KeyError:
            resp = yield from err_json(mode, False, "Source IP selected doesn't exist!")
    
    elif mode == "integ_check":
        try:
            resp = {"data": data["data"]}
        except KeyError:
            resp = yield from err_json(mode, False, "An error occurred while processing input data!")
    
    elif mode == "list_src":
        try:
            temp = []
            for src in sources:
                temp.append(src)
            resp = {"ips": temp}
        except KeyError:
            resp = yield from err_json(mode, False, "An error occurred while processing input data!")

    elif mode == "sense":
        try:
            read = data["pins"]
            sense = {}
            # Send 192 + pin num to read the bit.
            for i in read:
                pinNum = input_assign[i]
                send = 192 + pinNum
                iic.write_byte(address, send)
                time.sleep(0.2)
                sense[i] = int((iic.read_byte(address) / 255) * board_voltage)
                time.sleep(0.2)

            resp = \
                {
                    "voltageRef": board_voltage,
                    "pins": {},
                }
 
            for key in sense:
                resp["pins"][key] = sense[key]

        except KeyError:
            resp = yield from err_json(mode, False, "An error occurred while processing input data!")    
    
    else:
        resp = yield from err_json(mode, False, "Could not find a way to respond to the request!")

    # Success message and initial request information
    if "error_message" not in resp.keys():
        resp["success"] = True
        resp["init_req"] = mode

    resp = json.dumps(resp)

    print("RESPONSE >>", resp, "\n"); return resp
    
"""
    Processing client requests without a response, i.e. keyboard input
    Usually, this kind of input gets sent to the System Controller.
"""
@asyncio.coroutine
def processor(data):
    
    print("PROCESS  >>", data)
    mode = data["mode"]

    if mode == "keyboard":
        print("Format", data["format"])
        if data["format"] == "js":
            new_list = []
            for i in data["keys"]:
                if i in convert_keycode:
                    new_list += [convert_keycode[i]]
                elif i >= 65 and i <= 90:
                    new_list += [i+32]
                else:
                    new_list += [i]


            for i in new_list:
                print(new_list)
                with SMBusWrapper(bus_no) as bus:
                    bus.write_i2c_block_data(address, 0, new_list)

    if mode == "control":
        
        pinNum = output_assign[data["pin"]]
        
        for i in data["command"]:
            
            output = 0

            if type(i) == bool:
                if i == True:
                    output += 128
            elif type(i) == int:
                time.sleep(i/1000)
                continue
            else:
                print("Error!")

            output = output + pinNum
		
            print(">> OUTPUT", output)
            iic.write_byte(address, output)

            time.sleep(0.1)

@asyncio.coroutine
def hello(websocket, path):
    while True:
        message = yield from websocket.recv()
        # Preprocessing of data; string to JSON
        data = yield from preprocessor(message)
        if "error" in data.keys():
            print("An error occurred:", data["error"])
            continue
        # Look up request type and act accordingly
        if respond[data["mode"]] == True:
            resp = yield from responder(data)
            yield from websocket.send(resp)
        
        else:
            yield from processor(data)

start_server = websockets.serve(hello, '0.0.0.0', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
print("Server started")
asyncio.get_event_loop().run_forever()
