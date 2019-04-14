#!/usr/bin/env python

import asyncio, websockets
import ssl, pathlib
import json
import time

# Example list of sources for testing purposes
sources = \
    {
        "1.2.3.4": {
            "hostname": "helloworld",
            "video": {
                "url": "http://1.2.3.4/stream/",
                "format": "mjpg",
            },  
            "vnc": {
                "url": "http://1.2.3.4/vnc/",
            }
        },

        "5.6.7.8": {
            "hostname": "test",
            "video": {
                "url": "http://5.6.7.8/stream/",
                "format": "mjpg",
            },
            "vnc": {
                "url": "http://5.6.7.8/vnc/",
            }
        },

        "254.254.254.254": {
            "hostname": "test2",
            "video": {
                "url": "http://254.254.254.254/stream/",
                "format": "mjpg",
            },
            "vnc": {
                "url": "http://254.254.254.254/vnc/"
            }
        }

    }

respond = \
    {
        "change_src": True,
        "list_src": True,
        "integ_check": True,
        "get_addr": True,
        "keyboard": False,
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


    print("REQUEST  >>", data)
    

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

start_server = websockets.serve(hello, 'localhost', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()