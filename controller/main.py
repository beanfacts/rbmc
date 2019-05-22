#!/usr/bin/env python

import asyncio, websockets
import ssl, pathlib
import json
import time

from smbus import SMBus, SMBusWrapper
bus_no = 0
iic = SMBus(bus_no)
address = 0x04

# Example list of sources for testing purposes
sources = \
    {
        "rBMC Demo Machine": {
            "hostname": "rbmc-target",
            "video": {
                "url": "http://192.168.1.110:7070/javascript_simple.html",
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

async def err_json(mode, status, message):
    if status == False:
        return {"init_req": mode, "success": status, "error_message": message}

# Converting recieved string data to JSON format
async def preprocessor(message):
    try:
        formatted_message = json.loads(message)
        return formatted_message
    except json.decoder.JSONDecodeError:
        print("Server sent invalid data!")
        return {"error": "json decoder error"}

# Responding to client requests
async def responder(data):
    global sources
    mode = data["mode"]
    print("REQUEST  <<", data)
    if mode == "change_src":
        source_ip = data["source_ip"]
        try:
            resp = sources[source_ip]
            resp["source_ip"] = source_ip
        except KeyError:
            resp = await err_json(mode, False, "Source IP selected doesn't exist!")
    
    elif mode == "integ_check":
        try:
            resp = {"data": data["data"]}
        except KeyError:
            resp = await err_json(mode, False, "An error occurred while processing input data!")
    
    elif mode == "list_src":
        try:
            temp = []
            for src in sources:
                temp.append(src)
            resp = {"ips": temp}
        except KeyError:
            resp = await err_json(mode, False, "An error occurred while processing input data!")

    elif mode == "keyboard":
        if data["format"] == "js":
            new_list = []
            for i in data["keys"]:
                if i in convert_keycode:
                    new_list += convert_keycode[i]
                elif i >= 65 and i <= 90:
                    new_list += [i+32]
                else:
                    new_list += [i]

            for i in new_list:
                print(new_list)
                with SMBusWrapper(bus_no) as bus:
                    bus.write_block_data(address, 0, new_list)

    else:
        resp = await err_json(mode, False, "Could not find a way to respond to the request!")

    if "error_message" not in resp.keys():
        resp["success"] = True
        resp["init_req"] = mode

    resp = json.dumps(resp)

    print("RESPONSE >>", resp, "\n"); return resp
    
"""
    Processing client requests without a response, i.e. keyboard input
    Usually, this kind of input gets sent to the System Controller.
"""
async def processor(data):
    print("PROCESS  >>", data)

async def hello(websocket, path):
    async for message in websocket:
        
        # Preprocessing of data; string to JSON
        data = await preprocessor(message)
        if "error" in data.keys():
            print("An error occurred:", data["error"])
            continue
        # Look up request type and act accordingly
        if respond[data["mode"]] == True:
            resp = await responder(data)
            await websocket.send(resp)
        
        else:
            await processor(data)

start_server = websockets.serve(hello, '0.0.0.0', 8765)
print("Server started!")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()